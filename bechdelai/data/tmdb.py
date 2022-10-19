"""Function to get data from TMDB API
"""
import urllib
import requests
import pandas as pd
import os
from PIL import Image
from tqdm.auto import tqdm
from os import environ
from io import BytesIO
from dotenv import load_dotenv
from .scrap import get_json_from_url


class APIKeyNotSetInEnv(Exception):
    """Exception class for API key not set"""

    pass


try:
    # load .env file
    load_dotenv()
    API_KEY = environ["TMDB_API_KEY"]
except:
    raise APIKeyNotSetInEnv(
        "You need to set your TMDB API key into a .env file. `TMDB_API_KEY=<API_KEY>` "
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
        poster_url = f"{IMG_URL}/" + movie["poster_path"]
        title = movie["original_title"]
        year = movie["release_date"][:4]

        html = FORMAT_SUGG_HTML.format(
            href=href, poster_url=poster_url, title=title, year=year
        )
        format_res.append((html, movie_id))

    return format_res



def get_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

def get_poster_image_from_url(url):

    if not url.startswith("https"):
        url = f'https://image.tmdb.org/t/p/original{url}'
    
    img = get_image_from_url(url)
    return img


def get_movie_details_from_imdb_id(imdb_id):
    url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={API_KEY}&external_source=imdb_id"
    r = requests.get(url).json()
    return get_movie_details_from_id(r["movie_results"][0]["id"])


def get_poster_image(movie_id,as_img = True,backdrop = False):

    details = get_movie_details_from_id(movie_id)
    path = details["poster_path"] if backdrop == False else details["backdrop_path"]
    poster_path = f'https://image.tmdb.org/t/p/original{path}'

    if as_img:
        img = get_image_from_url(poster_path)
        return img
    else:
        return poster_path




def discover_movies(**kwargs) -> dict:
    """
    Tutorial on discover API
    - https://developers.themoviedb.org/3/discover/movie-discover
    - https://www.themoviedb.org/talk/5f60b26c706b9f0039076517
    - https://www.themoviedb.org/documentation/api/discover

    Example Query String
    primary_release_year=2020&with_original_language=hi|kn|ml|ta|te

    """

    query_string = urllib.parse.urlencode(kwargs)

    url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&language=en-US&{query_string}"
    r = requests.get(url).json()
    return r


def discover_all_movies(with_original_language = "fr",start_year = None,end_year = None,year = None,min_vote_count = 0,pages = 1000,sort_by = "popularity.desc"  ,**kwargs):

    data = []

    for i in tqdm(range(pages)):

        query = {
            "with_original_language":with_original_language,
            "vote_count.gte":min_vote_count,
            "page":i+1,
            "sort_by":sort_by,
            **kwargs
        }

        if year is not None: query["primary_release_year"] = year
        if start_year is not None: query["primary_release_date.gte"] = start_year
        if end_year is not None: query["primary_release_date.lte"] = end_year

        r = discover_movies(**query)
        if i == 0: 
            print(f'{r["total_results"]} Results in total and {r["total_pages"]} pages')
            print(query)

        data.extend(r["results"])

    data = pd.DataFrame(data)
    return data


def download_all_posters(movies,folder):
    """
    Input is dataframe from discover all movies function
    """

    if not os.path.exists(folder):
        os.mkdir(folder)

    # Save metadata as csv
    movies.to_excel(os.path.join(folder,"MOVIES_METADATA.xlsx"))

    for i in tqdm(range(len(movies))):
        row = movies.iloc[i]
        movie_id = row["id"]
        path = row["poster_path"]
        poster_path = f'https://image.tmdb.org/t/p/original{path}'
        path = os.path.join(folder,f"{movie_id}.png")
        if not os.path.exists(path):
            try:
                img = get_image_from_url(poster_path)
                img.save(path)
            except:
                print(f"Skipped movie {i}")