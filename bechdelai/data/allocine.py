"""Function to scrap allociné data
"""
import math

import pandas as pd
from bs4 import BeautifulSoup

from bechdelai.data.scrap import get_data_from_url
from bechdelai.data.scrap import RequestException
from bechdelai.data.src import load_allocine_filters
from bechdelai.data.tmdb import get_movie_cast_from_id
from bechdelai.data.tmdb import search_movie_from_query

# Url to scrap Allociné website
BASE_URL = "https://www.allocine.fr/"
QUERY_URL = f"{BASE_URL}films/{{sort_by}}{{genre_filter}}{{pays_filter}}{{decennie_filter}}{{annee_filter}}?page={{page_num}}"

# Default filters applies in QUERY_URL
DEFAULT_FILTERS = {
    "genre_filter": "",
    "pays_filter": "",
    "decennie_filter": "",
    "annee_filter": "",
    "page_num": "1",
}

# Map sorting names with url
VALID_SORT_BY = {
    "popularity": "",
    "alphabetic": "alphabetique/",
    "press_note": "presse/",
    "public_note": "notes/",
}

# Get all available filters
ALLOCINE_FILTERS = load_allocine_filters()
GENRE_FILTER = "genres"
DECADE_FILTER = "décénnies"
YEAR_FILTER = "années"
COUNTRY_FILTER = "pays"

# Maximum movies in a Allociné page
N_MAX_MOVIES_PAGE = 15


def get_file_content(fpath: str, **kwargs) -> str:
    """Get content from a file given a path

    Parameters
    ----------
    fpath : str
        file path

    Returns
    -------
    str
        file content
    """

    with open(fpath, **kwargs) as f:
        txt = f.read()

    return txt


def get_year_filter(decade_filters):
    """Returns year filters given the decade filters

    Example: for year 2015 -> "decennie-2010/annee-2015"
    """
    year_filters = []

    for decade in decade_filters:
        min_, max_ = decade["name"].split(" - ")

        for year in range(int(min_), int(max_) + 1):
            year_filters.append(
                {"filter": decade["filter"] + f"/annee-{str(year)}", "name": str(year)}
            )

    return year_filters


def get_allocine_filters(filters_path: str) -> dict:
    """Get filters page and category to prepare movie scraping
    with filters.

    The path must contains loaded HTML code get with inspect tool from
    https://www.allocine.fr/films/ (div with id "filter-entity")

    Parameters
    ----------
    filters_path : str
        Path to html of filters

    Returns
    -------
    dict
        Dictionnary with filter type as key and a list a dictionnary
        two keys: "filter" with string for url and "name" for
        user friendly choice
    """

    html = get_file_content(filters_path, encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    filter_list = soup.find("div", {"id": "filter-entity"})
    filters = filter_list.find_all("ul", {"class": "filter-entity-word"})

    filters_allocine = {}
    for filter_entity in filters:
        filter_name = filter_entity.get("data-name")
        items = filter_entity.find_all("a")
        item_details = []

        for item in items:
            detail = {
                "filter": item.get("href").split("/")[-2],
                "name": item.get("title"),
            }
            item_details.append(detail)

        filters_allocine[filter_name] = item_details

    filters_allocine["Année"] = get_year_filter(
        filters_allocine["Par années de production"]
    )

    return filters_allocine


def format_movies(movies_html):
    """Given html for each movie get from the film allociné page
    retrieve all information such as the title, img, url, director

    Parameters
    ----------
    movies_html : list
        Movie elements (parsed with bs4) from allociné page

    Returns
    -------
    list(dict)
        formated movie as dictionnaries
    """

    formated_movies = []
    for html in movies_html:
        img = html.find("img").get("src")

        if not (img.endswith(".jpg") or img.endswith(".png")):
            img = html.find("img").get("data-src")

        title = html.find("a", {"class": "meta-title-link"}).text
        url = html.find("a", {"class": "meta-title-link"}).get("href")
        url = f"{BASE_URL}{url}"

        date = html.find("span", {"class": "date"})
        year = None
        if date is not None:
            date = date.text
            year = date.split(" ")[-1]

        director = html.find("div", {"class", "meta-body-direction"})
        if director is not None:
            director = director.text.replace("\n", "").replace("De", "").strip()

        formated_movies.append(
            {
                "title": title,
                "img_path": img,
                "url": url,
                "year": year,
                "director": director,
            }
        )

    return formated_movies


def get_allocine_movies_from_one_page(
    filters: dict, sort_by="popularity", verbose=False
):
    """Returns all available movies in an Allociné film page
    that is scraped with wanted filters

    Parameters
    ----------
    filters : dict
        List of filters for the wanted search
        Available keys for filter are:
        "genre_filter", "pays_filter", "decennie_filter", "annee_filter", "page_num"
    sort_by : str, optional
        How to sort results, by default "popularity"
    verbose : bool, optional
        Whether to show verbosity or not, by default False

    Returns
    -------
    list(dict)
        formated movie as dictionnaries with title, url, img, director and date

    Raises
    ------
    ValueError
        `sort_by` is not valid
    RequestException
        Request response is not valid
    """

    if sort_by not in VALID_SORT_BY:
        raise ValueError(
            f"`sort_by` is not valid. It must be one of the following: %s"
            % (list(VALID_SORT_BY.keys()))
        )

    if "annee_filter" in filters:
        filters["decennie_filter"] = ""

    filters = {**DEFAULT_FILTERS, **filters, "sort_by": VALID_SORT_BY[sort_by]}

    for f, v in filters.items():
        if ("filter" in f) and (not v.endswith("/")) and (v != ""):
            filters[f] = f"{v}/"

    url = QUERY_URL.format(**filters)

    if verbose:
        print(f"Scrap url: {url}")

    ans = get_data_from_url(url)

    if ans.status_code != 200:
        raise RequestException(
            "Request response is not valid (status code %s)" % ans.status_code
        )

    html = BeautifulSoup(ans.text, "html.parser")

    movies_html = html.find_all("li", {"class": "mdl"})

    movies = format_movies(movies_html)

    return movies


def _check_filter_validity(val, key):
    """Checks that the filter value is available in the filter dictionnary"""
    elements = ALLOCINE_FILTERS[key]
    valid_values = list(elements.keys())
    val = str(val)

    if val not in [""] + valid_values:
        raise ValueError(
            f"For `{key}` the value is not valid, please choose one of the following: {valid_values}"
        )

    if val == "":
        return ""

    return elements[val]


def get_movies(
    n_movies=10,
    genre="",
    decade="",
    year="",
    country="",
    sort_by="popularity",
    verbose=True,
):
    """Returns `n_movies` for wanted filters sorted by `sort_by`

    Parameters
    ----------
    n_movies : int, optional
        number of movies wanted, by default 10
    genre : str, optional
        Filter for genre if "" then no filter, by default ""
    decade : str, optional
        Filter for decade if "" then no filter, by default ""
    year : str, optional
        Filter for year if "" then no filter, by default ""
    country : str, optional
        Filter for country if "" then no filter, by default ""
    sort_by : str, optional
        How to sort results, by default "popularity"
    verbose : bool, optional
        Whether to show verbosity or not, by default True

    Returns
    -------
    list(dict)
        formated movie as dictionnaries with title, url, img, director and date
    """

    filters = {}
    filters["genre_filter"] = _check_filter_validity(genre, key=GENRE_FILTER)
    filters["decennie_filter"] = _check_filter_validity(decade, key=DECADE_FILTER)
    filters["annee_filter"] = _check_filter_validity(year, key=YEAR_FILTER)
    filters["pays_filter"] = _check_filter_validity(country, key=COUNTRY_FILTER)

    n_pages = math.ceil(n_movies / N_MAX_MOVIES_PAGE)

    movies = []
    for num_page in range(1, n_pages + 1):
        _filters = {**filters, "page_num": str(num_page)}

        page_movies = get_allocine_movies_from_one_page(_filters, sort_by, verbose)

        if len(page_movies) + len(movies) > n_movies:
            _max = n_movies - len(movies)
            movies.extend(page_movies[:_max])
        else:
            movies.extend(page_movies)

        if len(page_movies) < N_MAX_MOVIES_PAGE:
            break

    return movies


def get_tmdb_id(movie_dict: dict):
    """Retrieves TMDB id from a formated allociné result

    Query by title, if year is the same then take this movie
    else if the director are the same then take this movie

    Parameters
    ----------
    movie_dict : dict
        formated movie from Allociné page

    Returns
    -------
    int
        TMDB id (or None if nothing found)
    """

    title = movie_dict["title"]
    year = movie_dict["year"]
    director = movie_dict["director"].split(",")[0]

    data = search_movie_from_query(title)

    for res in data["results"]:
        if res["release_date"][:4] == str(year):
            return res["id"]

        if director is None:
            continue

        details = get_movie_cast_from_id(res["id"])
        crew_df = pd.DataFrame(details["crew"])
        dir_name = "".join(crew_df.loc[crew_df["job"] == "Director"]["name"])

        if director in dir_name:
            return res["id"]

    return None


def get_tmdb_ids(movies: list) -> list:
    """Returns list of TMDB ids given a list of
    movies returned by `get_movies()`

    Parameters
    ----------
    movies : list
        list of dictionnary returned by `get_movies()`

    Returns
    -------
    list
        List of TMDB ids for each movie
    """
    ids = []
    for movie_dict in movies:
        try:
            ids.append(get_tmdb_id(movie_dict))
        except:
            print("Error when try to get TMDB ID for '%s'" % movie_dict["title"])

    return ids
