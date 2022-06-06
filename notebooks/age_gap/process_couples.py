import sys
sys.path.append("..\..")
import bechdelai.data.wikipedia as wiki
import bechdelai.data.tmdb as tmdb

import numpy as np
from datetime import datetime
import re
import pandas as pd

import spacy
from transformers import pipeline


def age(birthdate,release_date):
    """
    Compute age at release_date for a person born in birthdate
    Parameters
    ----------
    birthdate : datetime
    release_date : datetime


    Returns
    -------
    int
        age in years

    """
    # Difference in years
    year_difference = release_date.year - birthdate.year

    # Check if birthday happened before or after release date
    one_or_zero = ((release_date.month, release_date.day) < (birthdate.month, birthdate.day))

    # If release before birthday -> substract 1
    # If release after birthday -> substract 0
    age = year_difference - one_or_zero

    return age

def compute_cast_age(cast_df,release_date):
    """
    Compute age at release_date for each actor/actress in the cast_df
    Parameters
    ----------
    cast_df : DataFrame
                should contain the collumn id with the TMDB id of each actor/actress
    release_date : datetime


    Returns
    -------
    numpy.ndarray
        with age in years for each person in cast_df (None if birthday is not available)

    """
    age_at_release = np.repeat(None,len(cast_df))
    for i,row in cast_df.iterrows():
        birthday = tmdb.get_person_details_from_id(row['id'])['birthday']
        try:
            age_at_release[i] = age(datetime.strptime(birthday, '%Y-%m-%d'),release_date)
        except TypeError:
            age_at_release[i] = None
    return age_at_release

def get_character_from_wikipedia(star_name,cast_wiki):
    """
    Get the name of the character as it is presented in the Wikipedia Cast section.

    Parameters
    ----------
    star_name : str
                the name of the movie star
    cast_wiki : str
                the cast description from Wikipedia


    Returns
    -------
    str
        The name of the character played by movie_star as written in Wikipedia

    """
    pattern = '('+star_name+' (as|-|–) )(.+?)(,|:|\n)'
    match = re.search(pattern,cast_wiki)
    if match==None:
        return None
    return match[3]

def get_cast_from_wikipedia(title,release_year):
    """
    Get the cast section from Wikipedia page for movie title.
    In case of ambiguous pages in Wikipedia, the release_year may be needed to find the right page.


    Parameters
    ----------
    title : str
                the name of the movie
    release_year : int
                the year of movie release


    Returns
    -------
    str
        the cast description from Wikipedia.
        Return None if Cast section not found

    """
    for query_suffix in [' ('+str(release_year)+' film)',' (film)','']:
        try:
            return wiki.get_section_text(title+query_suffix, ['Cast'])['Cast']  # to improve
        except (ValueError,KeyError):
            continue
    return None

def correct_cast_with_wikipedia(tmdb_cast,wiki_cast):
    """
    Correct the characters' names in tmdb_cast if its written in a different form in Wikipedia.


    Parameters
    ----------
    tmdb_cast : DataFrame
                cast data from TMDB
    wiki_cast : str
                cast data from Wikipedia


    Returns
    -------
    DataFrame
        the cast description from Wikipedia.
        Return None if Cast section not found

    """
    # Get character's name that are different in TMDB and Wikipedia
    for i,star_name in tmdb_cast.name.items():
        character_wiki = get_character_from_wikipedia(star_name,wiki_cast)
        if character_wiki!=None:
            tmdb_cast.loc[i,'character'] = character_wiki.replace('"',"'")
    return tmdb_cast

def detect_relationship(character,verb,context,qa=None):
    """
    Answers the question 'Who {} {}?'.format(verb,character)


    Parameters
    ----------
    character : str
                name of the character
    verb : str
                sentence that is used to build the question
    context : str
                Text used as context for question answering
    qa : pipeline
                If None, pipeline is created in the function


    Returns
    -------
    str
        the answer for the question
    float
        the score given for the answer

    """
    if qa==None:
        # Load model
        nlp = spacy.load('en_core_web_lg')
        model_name = "deepset/roberta-base-squad2"

        qa = pipeline('question-answering', model=model_name, tokenizer=model_name, top_k=1)

    # Only ask question when the character is mentionned in the context
    if not character_is_mentionned(character,context):
        return None,np.nan

    QA_input = {
        'question': 'Who {} {}?'.format(verb,character),
        'context': context
    }
    a = qa(QA_input)

    # The answer should contain a single character. If it's not the case, the answer is not accepted
    if ' and ' in a['answer']:
        return None,np.nan
    # Ignore if detected couple is twice the same character
    if character==a['answer']:
        return None,np.nan

    return a['answer'],a['score']

def get_character_nickname(name):
    """
    Characters' names as they are extracted from TMDB can be formatted in different ways.
    When characters are refered by a nickname, it's commonly presented between \' or \"

    """
    nickname = re.search(r'(\'|\")(.*?)(\'|\")',name)
    if nickname != None:
        name = nickname.group(2)
    return name

def get_actor_from_character(cast_data,character):
    """
    Find in cast_data the actor/actress who played the character

    Parameters
    ----------
    cast_data : DataFrame
                cast data
    character : str
                name of the character to search


    Returns
    -------
    str or list
        the name(s) of the actor/actress that players the character

    """
    # to be sure that regex works, remove parenthesis
    character = character.replace('(','')
    character = character.replace(')','')
    character = character.replace('"',"'")# only use '

    # look for character's name match with all names in character (consider that middle names can be missing from character)
    pattern = '\s.*'.join(character.split(' '))+'.?(?:\s|$)'
    # \s makes sure name ends (so characters like Phuong's Sister, Franz's girlfiend are not included)
    actor = cast_data[cast_data.character.str.contains(pattern)]['name'].values
    actor_id = cast_data[cast_data.character.str.contains(pattern)]['id'].values

    if not len(actor):
        # character name with all names not found in cast_data
        for character_name in character.split(' '):
            pattern = character_name+'(?:\s|$)'
            actor = cast_data[cast_data.character.str.contains(pattern)]['name'].values
            actor_id = cast_data[cast_data.character.str.contains(pattern)]['id'].values
            if len(actor):
                break

    if not len(actor):
        # character's name still not found
        return None,None
    elif len(actor)==1:
        # only one actor corresponding to character
        return actor[0], actor_id[0]
    else:
        # multiple actors/resses, return as a list
        return list(actor),list(actor_id)


def get_age_gap(cast_data,couple):

    # If any of the actor/actress in the couple was not identified (None), return None
    if (couple[0]==None) | (couple[1]==None):
        return None, None

    # To compute the age gap, we must have identified exactly 1 actor/actress for each character (that are not the same)
    if (type(couple[0])==list) | (type(couple[1])==list) | (couple[0]==couple[1]):
        return None, None

    # get data for each person
    person0 = cast_data[cast_data.name==couple[0]]
    if not len(person0):
        return None, None
    age0 = person0.age_at_release.values[0]
    gender0 = person0.gender.values[0]

    person1 = cast_data[cast_data.name==couple[1]]
    if not len(person1):
        return None, None
    age1 = person1.age_at_release.values[0]
    gender1 = person1.gender.values[0]

    # if age is not defined for any person
    if (age0==None) | (age1==None):
        return None,[gender0,gender1]

    # if both are from same gender, use absolute difference
    if gender0==gender1:
        return abs(age0-age1),[gender0,gender1]
    else:
        return abs(age0-age1),[gender0,gender1]

def character_is_mentionned(character_name,text):
    '''
    Check if any part of the character's name is mentionned in the text given
    '''
    for name_part in character_name.split(' '):
        match = re.search(r'\b'+name_part+r'\b',text)
        if not match==None:
            return 1
    return 0

def remove_players_from_text(cast_names,text):
    '''
    Remove mentions to the actors and actresses names in the Wikipedia plot as it may confuse the question answering algorithms
    '''
    for name in cast_names:
        text = re.sub('(\('+name+'\))', '', text)
    return text



def fill_scores(df, new_entry, column_to_update):
    '''
    This function adds the new_entry in the DataFrame df.
    If the couple_actors in new_entry already exists in df, update the score in the column_to_update.
    Else, add a new role, with all data in new_entry.
    '''
    # was this couple previously detected?
    couple_actors = new_entry['actors']
    couple_in_df = [((row.actors==couple_actors) or (row.actors==couple_actors[::-1])) and (row.movie==movie) for i,row in df.iterrows()]

    if sum(couple_in_df): # if this couple appeared before
        previous_score = df.loc[couple_in_df,v].iloc[0]
        df.loc[couple_in_df,column_to_update] = np.nanmax([previous_score,new_entry[column_to_update]])
    else: # if it is the first time a couple appears
        df = pd.concat([df,pd.Series(new_entry).to_frame().T], ignore_index=True)
    return df


def compute_relationships_in_movie(cast_data,document_string, verbs):

    # Load model
    nlp = spacy.load('en_core_web_lg')
    model_name = "deepset/roberta-base-squad2"

    qa = pipeline('question-answering', model=model_name, tokenizer=model_name, top_k=1)

    ans = pd.DataFrame(columns = ['character1','star1','star_id1','character2','star2','star_id2','age_gap','genders','question','score'])
    people = [get_character_nickname(name) for name in cast_data.character]

    # Prediction -> Combine characters and questions
    for context in document_string.split('\n'):
        if not len(context):
            continue
        for v in verbs:
            for person1 in people:

                person2, score = detect_relationship(person1,v,context,qa)
                if person2==None:
                    continue

                # create new entry in ans dataframe
                star1,star_id1 = get_actor_from_character(cast_data,person1)
                star2,star_id2 = get_actor_from_character(cast_data,person2)
                # compute age gap
                age_gap,genders = get_age_gap(cast_data,[star1,star2])
                # ignore entry if age gap not computed
                if age_gap==None:
                    continue

                new_entry = {'character1':person1,
                             'star1':star1,
                             'star_id1':star_id1,
                             'character2':person2,
                             'star2':star2,
                             'star_id2':star_id2,
                             'age_gap':age_gap,
                             'genders':genders,
                             'question':v,
                             'score':score}

                ans = pd.concat([ans,pd.Series(new_entry).to_frame().T], ignore_index=True)
    return ans
