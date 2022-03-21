"""Function to get data from TMDB API
"""
from os import environ

from dotenv import load_dotenv

from bechdelai.data.scrap import get_data_from_url
from bechdelai.data.scrap import RequestException


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


def _get_json_from_url(url):
    """Get json results from an endpoint"""
    ans = get_data_from_url(url)

    if ans.status_code != 200:
        raise RequestException(f"Status code different from 200, got {ans.status_code}")

    data = ans.json()

    return data


def search_movie_from_query(query: str) -> dict:
    """Get TMDB API result for search movie endpoint given a query

    Parameters
    ----------
    query : str
        Movie query to research
    """
    url = SEARCH_API_URL.format(query=query)

    return _get_json_from_url(url)


def get_movie_details_from_id(movie_id) -> dict:
    """Get TMDB API result for movie details endpoint given an id

    Parameters
    ----------
    movie_id : str or int
        Movie id to get details from
    """
    url = MOVIE_API_URL.format(movie_id=str(movie_id))

    return _get_json_from_url(url)


def get_movie_cast_from_id(movie_id) -> dict:
    """Get TMDB API result for movie cast endpoint given an id

    Parameters
    ----------
    movie_id : str or int
        Movie id to get cast from
    """
    url = CAST_API_URL.format(movie_id=str(movie_id))

    return _get_json_from_url(url)


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
