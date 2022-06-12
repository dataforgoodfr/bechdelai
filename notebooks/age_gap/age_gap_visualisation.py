import sys
sys.path.append("../..")
from age_gap_automation import Movie
import process_couples as pc
import bechdelai.data.wikipedia as wiki
import bechdelai.data.tmdb as tmdb

import streamlit as st
import pandas as pd
import plotly.express as px

MOVIE_FILES = {"Harry Potter and the Goblet of Fire":"hp4.csv",
               "Call me by your name":"call_me.csv",
               "The Big Lebowski":"lebowski.csv",
               "Love Actually":"love_actually.csv"}
MOVIE_YEARS = {"Harry Potter and the Goblet of Fire":2005,
              "Call me by your name":2017,
              "The Big Lebowski":1998,
              "Love Actually":2003}

VERBS = ['kisses', 'sleeps with', 'goes on a date with', 'has sex with', 'marries', 'is in love with','is in couple with', 'is the father of', 'is the mother of']
LOVE_VERBS = ['kisses', 'sleeps with', 'goes on a date with', 'has sex with', 'marries', 'is in love with','is in couple with']

@st.cache
def load_data_from_file(file):
    return pd.read_csv(file)
def load_data(movie):
    return pc.compute_relationships_in_movie(movie.cast,movie.plot, VERBS)


def main():
    st.set_page_config(layout="wide")
    title = st.selectbox("Choose a movie:",list(MOVIE_FILES.keys()))
    st.title(title)
    st.subheader('Romantic relationships')


    movie = Movie(title,MOVIE_YEARS[title])
    cast = movie.cast

    try:
        scores = load_data_from_file(MOVIE_FILES[title])
    except FileNotFoundError:
        with st.spinner('Wait for it...'):
            scores = load_data(movie)

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



        st.subheader('{} and {}'.format(star_younger['character'], star_older['character']))
        st.write('They were played by {} and {} respectively. '.format(star_younger['name'], star_older['name']))
        st.write('Age gap: ' ,row.age_gap)

        col1, col2, col3,col4,col5 = st.columns([1.5,5,1.5,2,10])
        col1.image('https://image.tmdb.org/t/p/original'+star_younger['image'],width=100)


        values = col2.slider(
             '',
             10, 50,
             (star_younger['age'], star_older['age']),
             disabled=True, key = "slider_"+str(i))

        col3.image('https://image.tmdb.org/t/p/original'+star_older['image'],width=100)

        # relationship_true = col4.radio('Is this relationship true?', ['Yes', 'No'],key = "radio_"+str(i))
        count+=1



if __name__ == "__main__":
    main()
