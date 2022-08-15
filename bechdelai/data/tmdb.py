"""Function to get data from TMDB API
"""
from os import environ

import pandas as pd
import numpy as np
from dotenv import load_dotenv

from bechdelai.data.scrap import get_json_from_url


class APIKeyNotSetInEnv(Exception):
    """Exception class for API key not set"""

    pass


import os

try:
    # load .env file
    load_dotenv(f"{os.getcwd()}/.env", verbose=True)
    load_dotenv()
    API_KEY = environ["TMDB_API_KEY"]
except:
    raise APIKeyNotSetInEnv(
        "You need to set your TMDB API key into a .env file in your current working directory.\n`TMDB_API_KEY=<API_KEY>`\n"
        + "To get a key please check directly on the website https://developers.themoviedb.org/3/getting-started/introduction"
    )

# main urls
MAIN_URL = "https://www.themoviedb.org"
IMG_URL = "https://image.tmdb.org/t/p/w94_and_h141_bestv2"

# Url for the API
API_URL = "https://api.themoviedb.org/3"
SEARCH_API_URL = f"{API_URL}/search/movie?api_key={API_KEY}&query={{query}}"
MOVIE_API_URL = f"{API_URL}/movie/{{movie_id}}?api_key={API_KEY}"
CAST_API_URL = f"{API_URL}/movie/{{movie_id}}/credits?api_key={API_KEY}"
PERSON_API_URL = f"{API_URL}/person/{{person_id}}?api_key={API_KEY}"
PERSON_IMG_API_URL = f"{API_URL}/person/{{person_id}}/images?api_key={API_KEY}"
SEARCH_IMDB_URL = (
    f"{API_URL}//find/tt{{imdb_id}}?api_key={API_KEY}&external_source=imdb_id"
)

# Html for suggestion diplays
FORMAT_SUGG_HTML = """
<tr>
    <td>
        <a href="{href}"><img src="{poster_url}"/></a>
    </td>
    <td>
        <a href="{href}">
            {title}
        </a> ({year})
    </td>
</tr>
"""


def search_movie_from_query(query: str) -> dict:
    """Get TMDB API result for search movie endpoint given a query

    You can find the website view with this url:
    https://www.themoviedb.org/search/movie?query=

    Parameters
    ----------
    query : str
        Movie query to research
    """
    url = SEARCH_API_URL.format(query=query)

    return get_json_from_url(url)


def get_movie_details_from_id(movie_id) -> dict:
    """Get TMDB API result for movie details endpoint given an id

    You can find the website view with this url (example for id 81):
    https://www.themoviedb.org/movie/81

    Parameters
    ----------
    movie_id : str or int
        Movie id to get details from
    """
    url = MOVIE_API_URL.format(movie_id=str(movie_id))

    return get_json_from_url(url)


def get_movie_cast_from_id(movie_id) -> dict:
    """Get TMDB API result for movie cast endpoint given an id

    You can find the website view with this url (example for id 81):
    https://www.themoviedb.org/movie/81/cast

    Parameters
    ----------
    movie_id : str or int
        Movie id to get cast from
    """
    url = CAST_API_URL.format(movie_id=str(movie_id))

    return get_json_from_url(url)


def get_id_from_imdb_id(imdb_id) -> int:
    """Get TMDB API result for movie cast endpoint given an id

    Parameters
    ----------
    imdb_id : str or int
        Movie id to get cast from
    """
    url = SEARCH_IMDB_URL.format(imdb_id=str(imdb_id))

    res = get_json_from_url(url)
    if len(res["movie_results"]) == 0:
        return None

    return res["movie_results"][0]["id"]

def get_person_details_from_id(person_id) -> dict:
    """Get TMDB API result for person details by id

    You can find the website view with this url (example for id 81):
    https://www.themoviedb.org/person/81

    Parameters
    ----------
    person_id : str or int
        Person id to get details from
    """
    url = PERSON_API_URL.format(person_id=str(person_id))

    return get_json_from_url(url)

def get_person_image_from_id(person_id) -> dict:
    """Get TMDB API images for person by id

    Parameters
    ----------
    person_id : str or int
        Person id to get details from
    """
    url = PERSON_IMG_API_URL.format(person_id=str(person_id))

    return get_json_from_url(url)

def format_results_for_suggestion(search_res: dict) -> list:
    """Format search movie results for `show_movie_suggestions()`

    Parameters
    ----------
    search_res : dict
        result of `search_movie_from_query()`

    Returns
    -------
    list
        List of formated tuple for displays.
        1st element is the html to display and the 2nd
        is the movie ID
    """
    if "results" not in search_res:
        raise ValueError("search_res must be the result of TMDB search movie endpoint")

    format_res = []
    # for each movie format is a tuple of
    # (html of the movie, movie id)
    for movie in search_res["results"]:
        movie_id = movie["id"]

        href = f"{MAIN_URL}/movie/{movie_id}"
        poster_url = f"{IMG_URL}/" + str(movie["poster_path"])
        title = movie["original_title"]
        year = movie["release_date"][:4]

        html = FORMAT_SUGG_HTML.format(
            href=href, poster_url=poster_url, title=title, year=year
        )
        format_res.append((html, movie_id))

    return format_res


def get_movies_from_ids(movie_ids: list) -> tuple:
    """Returns TMDB API return for all movie ID
    set in the input

    Get metadata from `get_movie_details_from_id()` function
    and cast and crew from `get_movie_cast_from_id()` function

    Parameters
    ----------
    movie_ids : list
        List of TMDB ids

    Returns
    -------
    tuple
        3 dataframes: movie details, crew and cast
    """
    metadata_df = []
    crew_df = []
    cast_df = []

    for movie_id in movie_ids:
        if movie_id is None:
            continue

        try:
            data = get_movie_details_from_id(movie_id)
        except:
            print(f"Error when try to get details for id:'{movie_id}'")
            continue

        metadata_df.append(data)

        try:
            data = get_movie_cast_from_id(movie_id)
        except:
            print(f"Error when try to get cast and crew for id:'{movie_id}'")
            continue

        _crew_df = pd.DataFrame(data["crew"])
        _crew_df["id"] = movie_id
        _cast_df = pd.DataFrame(data["cast"])
        _cast_df["id"] = movie_id

        crew_df.append(_crew_df)
        cast_df.append(_cast_df)

    movies_df = pd.DataFrame(metadata_df)
    crew_df = pd.concat(crew_df)
    cast_df = pd.concat(cast_df)

    return movies_df, crew_df, cast_df

def get_best_tmdb_id(title,release_year):
    """
    Get most probable TMDB id for movie title released in release year.
    The release_date in TMDB may be different from the release_year given, but we look for the closest date.

    Parameters
    ----------
    title : str
                movie title
    release_year : int
                year the movie was release


    Returns
    -------
    int
        TMDB id

    """
    movie_candidates = search_movie_from_query(title)
    if movie_candidates['total_results']==0:
        # Movie not found in TMDB with query
        return None

    if  release_year==None:
        return res[0]['id']
    else:
        # find most probable id -> same (or closest) release year
        movie_id = ''
        release_year_error = np.Inf # should be min
        # look at the 5 first matches to choose the one that was release closer to release_year
        for res in movie_candidates["results"][:5]:
            if ('release_date' not in res.keys()):
                continue
            try:
                res_release_year = int(res['release_date'][:4])
            except ValueError:
                continue
            if res_release_year==release_year:
                movie_id = res['id']
                break
            elif abs(res_release_year-release_year)<release_year_error:
                movie_id = res['id']
                release_year_error = abs(res_release_year-release_year)
    return movie_id
