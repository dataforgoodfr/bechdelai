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


@st.cache
def load_data_from_file(file):
    return pd.read_csv(file)
def load_data(movie):
    verbs = ['kisses', 'sleeps with', 'goes on a date with', 'has sex with', 'marries', 'is in love with','is in couple with', 'is the father of', 'is the mother of']
    return pc.compute_relationships_in_movie(movie.cast,movie.plot, verbs)


def main():
    st.set_page_config(layout="wide")
    title = st.selectbox("Choose a movie:",list(MOVIE_FILES.keys()))
    st.title(title)
    try:
        scores = load_data_from_file(MOVIE_FILES[title])
    except FileNotFoundError:
        with st.spinner('Wait for it...'):
            movie = Movie(title,MOVIE_YEARS[title])
            scores = load_data(movie)

    count=0
    for i,row in scores.sort_values('score',ascending=False).iterrows():

        if (count==10) | (row.score<0.3):
            break

        if ('mother' in row.question) | ('father' in row.question): # for parental relationship, the threshold is high
            if row.score < 0.9:
                continue
        st.subheader('{} {} {}'.format(row.character1, row.question, row.character2))
        st.write(row.score)

        col1, col2, col3,col4 = st.columns([3,3,2,10])
        img_star1 = tmdb.get_person_image_from_id(row.star_id1)
        col1.image('https://image.tmdb.org/t/p/original'+img_star1["profiles"][0]["file_path"],width=200)

        img_star2 = tmdb.get_person_image_from_id(row.star_id2)
        col2.image('https://image.tmdb.org/t/p/original'+img_star2["profiles"][0]["file_path"],width=200)

        relationship_true = col3.radio('Is this relationship true?', ['Yes', 'No'],key = "couple_"+str(i))
        count+=1



if __name__ == "__main__":
    main()
