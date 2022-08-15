
import sys
sys.path.append("../..")
from age_gap_automation import Movie
import process_couples as pc
import bechdelai.data.wikipedia as wiki
import bechdelai.data.tmdb as tmdb
from pyvis.network import Network
import numpy as np
import streamlit.components.v1 as components
from pyvis import network as net

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu


MOVIE_FILES = {"Harry Potter et la Coupe de Feu":"hp4.csv",
               "Call me by your name":"call_me.csv",
               "The Big Lebowski":"lebowski.csv",
               "Love Actually":"love_actually.csv"}
MOVIE_YEARS = {"Harry Potter et la Coupe de Feu":2005,
              "Call me by your name":2017,
              "The Big Lebowski":1998,
              "Love Actually":2003}
MOVIE_ORIG = {"Harry Potter et la Coupe de Feu":"Harry Potter and the Goblet of Fire",
             "Call me by your name":"Call me by your name",
             "The Big Lebowski":"The Big Lebowski",
             "Love Actually":"Love Actually"}

VERBS = ['kisses', 'sleeps with', 'goes on a date with', 'has sex with', 'marries', 'is in love with','is in couple with', 'is the father of', 'is the mother of']
LOVE_VERBS = ['kisses', 'sleeps with', 'goes on a date with', 'has sex with', 'marries', 'is in love with','is in couple with']

@st.cache(allow_output_mutation=True)
def load_data_from_file(file):
    return pd.read_csv(file)
@st.cache
def load_data(movie):
    return pc.compute_relationships_in_movie(movie.cast,movie.plot, VERBS)


# --------------- MENU SELECTION
def menu_horizontal():
	selected_info = option_menu(None,
		["Relations", "Couples", "Corrections"],
	    icons=['people', 'heart', "check-all",],
	    menu_icon="cast",
	    default_index=0,
	    orientation="horizontal",
	    styles={
	        "container": {"padding": "0!important", "background-color": "#fafafa"},
	        "icon": {"color": "#EEAE46", "font-size": "20px"},
	        "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
	        "nav-link-selected": {"background-color": "#D0DE5C"},
	    }
	)
	return selected_info

def create_network(cast,scores):
    # Define color by relationship type
    relationship_type = {'kisses':'love',
                          'sleeps with':'love',
                          'goes on a date with':'love',
                          'has sex with':'love',
                          'marries':'love',
                          'is in love with':'love',
                          'is in couple with':'love',
                          'is the father of':'family',
                          'is the mother of':'family',
                          'is the son of':'family',
                          'is the daughter of':'family',
                          'is a friend of':'friend',
                          'is in the family of':'family',
                          'is the enemy of':'enemy'}
    relationship_color = {'love':'#fca311',
                          'family':'#cce03d',
                          'friend':'#35c4d7',
                          'enemy':'#000000'}
    color_node = {0:'#187498',
                  1:'#F9D923',
                  2:'#36AE7C',
              3:'#EB5353'}

    g = Network('750px', '690px')

    # add nodes
    all_stars = np.unique(list(scores.star1.values)+list(scores.star2.values))
    for star in all_stars:
        star_data = cast[cast.name==star]
        character = star_data['character'].iloc[0]
        image_path = tmdb.get_person_image_from_id(star_data.id.iloc[0])
        try:
            image = 'https://image.tmdb.org/t/p/original'+image_path["profiles"][0]["file_path"]
        except IndexError:
            image = "http://cdn.onlinewebfonts.com/svg/img_233997.png"
        g.add_node(star,
                   label = character,
                   title = star,
                   shape='circularImage',
                   image =image,
    #                borderWidth=0, # without border
                   color = color_node[star_data['gender'].iloc[0]], # with color border by gender
                   borderWidth=3, # with color border
                   size = 30,
                   labelHighlightBold=True)

    # add edges
    for i,row in scores.iterrows():
        row_relation_type = relationship_type[row.question]
        title = "{} {} {}\n\n".format(row.character2,row.question,row.character1)+\
                "At movie release\n"+\
                '{} was {} years old \n'.format(row.star1,cast[cast.name==row.star1]['age_at_release'].iloc[0])+\
                '{} was {} years old \n'.format(row.star2,cast[cast.name==row.star2]['age_at_release'].iloc[0])


    #     if row_relation_type=='love': # is romantic relationship
    #         title = age_gap
        g.add_edge(row.star1,row.star2,
                   value=100*row.score,
                   color=relationship_color[row_relation_type],
                   title = title)
    return g

def do_relations(cast,scores):
    g = create_network(cast,scores)
    g.save_graph(f'relation_graph.html')
    # st.header('Connections by Company Graph')
    HtmlFile = open(f'relation_graph.html','r',encoding='utf-8')

    # Load HTML into HTML component for display on Streamlit
    components.html(HtmlFile.read(), height=800, width=800)

def get_scores(movie,title):
    try:
        scores = load_data_from_file(MOVIE_FILES[title])
    except FileNotFoundError:
        with st.spinner('Patientez...'):
            scores = load_data(movie)
    return scores

def do_couples(scores, cast):
    scores.sort_values('score',ascending=False,inplace=True)
    scores.drop_duplicates(['star1','star2'],keep='first',inplace=True) # TO DO: avoid duplicates when star1 and star2 are inversed

    count=0
    for i,row in scores.iterrows():

        if row.question not in LOVE_VERBS:
            continue

        if (count==10) | (row.score<0.7):
            break

        star_younger = {'name':row.star1,
                 'character':row.character1,
                 'age':cast[cast.name==row.star1]['age_at_release'].iloc[0],
                 'gender':cast[cast.name==row.star1]['gender'].iloc[0],
                 'image' : tmdb.get_person_image_from_id(row.star_id1)["profiles"][0]["file_path"] }
        star_older = {'name':row.star2,
                 'character':row.character2,
                 'age':cast[cast.name==row.star2]['age_at_release'].iloc[0],
                 'gender':cast[cast.name==row.star2]['gender'].iloc[0],
                 'image' : tmdb.get_person_image_from_id(row.star_id2)["profiles"][0]["file_path"] }

        if star_younger['age'] > star_older['age']:
            star_aux = star_younger
            star_younger = star_older
            star_older = star_aux



        st.subheader('{} et {}'.format(star_younger['character'], star_older['character']))
        st.write('Ces personnages ont été joués par {} et {} respectivement. '.format(star_younger['name'], star_older['name']))
        st.write('Ecart d\'âge: ' ,row.age_gap)

        col1, col2, col3 = st.columns([1.5,5,1.5])
        col1.image('https://image.tmdb.org/t/p/original'+star_younger['image'],width=100)


        values = col2.slider(
             '',
             10, 50,
             (star_younger['age'], star_older['age']),
             disabled=True, key = "slider_"+str(i))

        col3.image('https://image.tmdb.org/t/p/original'+star_older['image'],width=100)

        count+=1

def do_corrections(scores):
        count=0
        for i,row in scores.iterrows():

            if row.question not in VERBS:
                continue

            if (count==10):
                break

            if ('mother' in row.question) | ('father' in row.question): # for parental relationship, the threshold is high
                if row.score < 0.85:
                    continue
            st.subheader('{} {} {}'.format(row.character2, row.question, row.character1))
            st.write('Score: ',row.score)
            # st.write('Age gap: ' ,row.age_gap)

            col1, col2, col3 = st.columns([2,2,2])
            img_star2 = tmdb.get_person_image_from_id(row.star_id2)
            col1.image('https://image.tmdb.org/t/p/original'+img_star2["profiles"][0]["file_path"],width=150)

            img_star1 = tmdb.get_person_image_from_id(row.star_id1)
            col2.image('https://image.tmdb.org/t/p/original'+img_star1["profiles"][0]["file_path"],width=150)

            relationship_true = col3.radio('Is this relationship true?', ['Yes', 'No'],key = "couple_"+str(i))

            st.text("\n")
            count+=1


menu_nav_viz_dict = {
"Relations" : {"fn": do_relations},
"Couples" : {"fn": do_couples},
"Corrections" : {"fn": do_corrections},}


def main():
    st.set_page_config(layout="centered")
    title = st.selectbox("Choisissez un film:",list(MOVIE_FILES.keys()))
    # st.title(title)

    movie = Movie(MOVIE_ORIG[title],MOVIE_YEARS[title])
    cast = movie.cast
    scores = get_scores(movie,title)
    scores = scores.sort_values('score',ascending=False)

    selected_info= menu_horizontal()

    if selected_info in menu_nav_viz_dict.keys():
    	if selected_info == "Relations":
    		do_relations(cast,scores[scores.score>0.4])
    	elif selected_info == "Couples":
    		do_couples(scores,cast)
    	elif selected_info == "Corrections":
    		do_corrections(scores[scores.score>0.4])
    	else :
    		st.empty()

if __name__ == "__main__":
    main()
