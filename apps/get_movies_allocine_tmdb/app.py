"""Streamlit app to scrap allociné Data and get
TMDB details
"""
import base64
from time import time
from zipfile import ZipFile

import streamlit as st

from bechdelai.data.allocine import ALLOCINE_FILTERS
from bechdelai.data.allocine import get_movies
from bechdelai.data.allocine import get_tmdb_ids
from bechdelai.data.allocine import VALID_SORT_BY
from bechdelai.data.tmdb import get_movies_from_ids


@st.cache
def convert_df(df):
    """Convert df to csv string"""
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode("utf-8")


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
details_csv_name = "movies_details.csv"
crew_csv_name = "movies_crew.csv"
cast_csv_name = "movies_cast.csv"

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
        st.markdown("`#4` Ready to download dataframes")

        movies_csv = convert_df(movies_df)
        cast_csv = convert_df(cast_df)
        crew_csv = convert_df(crew_df)

    zip_name = "movies_datasets.zip"
    zip_file = ZipFile(zip_name, "w")
    zip_file.writestr(details_csv_name, movies_csv)
    zip_file.writestr(cast_csv_name, cast_csv)
    zip_file.writestr(crew_csv_name, crew_csv)
    zip_file.close()

    with open(zip_name, "rb") as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f"<a href=\"data:file/zip;base64,{b64}\" download='{zip_name}'>\
            Download movies datasets\
        </a>"
    st.sidebar.markdown(href, unsafe_allow_html=True)

    st.success("Done!")
