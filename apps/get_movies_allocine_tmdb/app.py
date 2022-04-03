"""Streamlit app to scrap allociné Data and get
TMDB details
"""
from os import abspath
from os import dirname
from time import time

import streamlit as st

from bechdelai.data.allocine import ALLOCINE_FILTERS
from bechdelai.data.allocine import get_movies
from bechdelai.data.allocine import get_tmdb_ids
from bechdelai.data.allocine import VALID_SORT_BY
from bechdelai.data.tmdb import get_movies_from_ids

# Write title
st.title("Allociné / TMDB Scraper")

# First details : number of movie wanted and sort by
col1, col2 = st.columns(2)
n_movies = col1.number_input("Number of movie wanted", min_value=1, step=1)
sort_by = col2.selectbox("Sort by", list(VALID_SORT_BY.keys()), index=0)

# Filters : Genres, years and countries
st.markdown("**Filters**")
col1, col2, col3 = st.columns(3)


def init_filters_selectbox(col, key):
    """Init filters"""
    options = [""] + list(ALLOCINE_FILTERS[key].keys())
    return col.selectbox(key, options, index=0)


genre = init_filters_selectbox(col1, "genres")
year = init_filters_selectbox(col2, "années")
country = init_filters_selectbox(col3, "pays")

# Get path where to save results
dir_path = dirname(abspath(__file__))
details_csv_name = "movies_details"
crew_csv_name = "movies_crew"
cast_csv_name = "movies_cast"

st.text_input("Directory to save results", value=dir_path)

details_df_path = f"{dir_path}/{details_csv_name}.csv"
crew_df_path = f"{dir_path}/{crew_csv_name}.csv"
cast_df_path = f"{dir_path}/{cast_csv_name}.csv"

# Section to show scraping results
st.markdown("## `Scraping`")

if st.button("Get movies..."):
    with st.spinner("Wait for it..."):
        t0 = time()
        st.write("`#1` get movies from allociné")

        movies = get_movies(
            n_movies=n_movies,
            genre=genre,
            country=country,
            year=year,
            sort_by=sort_by,
            verbose=True,
        )

        st.markdown("Allociné data retrieved after `%.1fsec`" % (time() - t0))
        st.markdown("`#2` match with TMDB ids")

        movies_id = get_tmdb_ids(movies)

        st.markdown("TMDB ids retrieved after `%.1fsec`" % (time() - t0))
        st.markdown("`#3` Get movie detail, cast and crew")

        movies_df, crew_df, cast_df = get_movies_from_ids(movies_id)

        st.markdown(
            "movie detail, cast and crew retrieved after `%.1fsec`" % (time() - t0)
        )
        st.markdown("`#4` Save dataframes")

        movies_df.to_csv(details_df_path, index=False)
        cast_df.to_csv(cast_df_path, index=False)
        crew_df.to_csv(crew_df_path, index=False)

        st.markdown(f"- movies_df save at `{details_df_path}`")
        st.markdown(f"- cast_df save at `{cast_df_path}`")
        st.markdown(f"- crew_df save at `{crew_df_path}`")

    st.success("Done!")
