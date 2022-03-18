import pandas as pd
import requests
from bs4 import BeautifulSoup
from IPython.display import display
from IPython.display import HTML
from numpy import character

MAIN_URL = "https://www.imdb.com"
URL_SEARCH = f"{MAIN_URL}/find?s=tt&q={{q}}"
DEFAULT_HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.5",
}


class RequestException(Exception):
    pass


def create_header(url: str) -> dict:
    """Create a header dictionnary if it need
    to be changed (e.g. for an API)
    Parameters
    ----------
    url : str
        url to request (needed to get the host)
    Returns
    -------
    dict
        header dictionnary
    Raises
    ------
    TypeError
        url must be a string
    ValueError
        url must start with 'http'
    """
    if not isinstance(url, str):
        raise TypeError("url must be a string")
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("url must start with 'http'")

    header = DEFAULT_HEADER

    url_split = url.split("//")
    http = url_split[0]
    host = url_split[1].split("/")[0]

    header["Host"] = host
    header["Referer"] = http + "//" + host
    header["Origin"] = http + "//" + host

    return header


def get_data_from_url(url: str) -> requests.Response:
    """Return answer of a request get
    from a wanted url
    Parameters
    ----------
    url : str
        url to request
    Returns
    -------
    requests.Response
        answer from requests.get function
    Raises
    ------
    TypeError
        url must be a string
    ValueError
        url must start with 'http'
    """

    if not isinstance(url, str):
        raise TypeError("url must be a string")
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("url must start with 'http'")

    headers = create_header(url)
    r = requests.get(url, headers=headers)

    return r


def preprocess_search_result_list(suggestions):
    """Preprocess list of results from suggest movies"""
    format_res = []
    for elem in suggestions:
        a = elem.find("a")

        html = str(elem)
        movie_url = MAIN_URL + a.get("href")
        movie_url = movie_url.split("?")[0] + "fullcredits"
        movie_id = movie_url.split("https://www.imdb.com/title/")[1].split("/")[0]

        format_res.append((html, movie_url, movie_id))

    return format_res


def find_movie_from_kerword(q):
    """Returns the list of best match from a query into
    IMDB website
    """
    url = URL_SEARCH.format(q=q)

    ans = get_data_from_url(url)

    if ans.status_code != 200:
        raise RequestException(
            "Request response is not valid (status code %s)" % ans.status_code
        )

    soup = BeautifulSoup(ans.text, "html.parser")
    res = soup.find_all("tr", {"class": "findResult"})

    res = preprocess_search_result_list(res)

    return res


def show_movie_suggestions(suggestions, top=None):
    """Show suggestions"""
    if top is not None:
        suggestions = suggestions[:top]

    for i, elem in enumerate(suggestions):
        display(HTML(f"{i} " + elem[0]))


def show_movie_suggestions_get_id(suggestions, top=None, verbose=True):
    """Show suggestions and returns wanted ID"""
    show_movie_suggestions(suggestions, top)

    print()
    idx = int(input("Select wanted index:"))

    if verbose:
        print("ID of the movie:", str(suggestions[idx][2]))
        print("URL of the casting:", suggestions[idx][1])

    return suggestions[idx][2], suggestions[idx][1]


def get_movie_details(url):
    """Get main details of a movie from url"""
    ans = get_data_from_url(url)
    soup = BeautifulSoup(ans.text, "html.parser")

    title = soup.find("h1").text

    info = soup.find("ul", {"data-testid": "hero-title-block__metadata"}).find_all("li")
    date = info[0].find("a").text
    duration = info[2].text

    return {"title": title, "date": date, "duration": duration}


def get_movie_casts(url):
    """Get casting of a movie with the url"""
    ans = get_data_from_url(url)
    soup = BeautifulSoup(ans.text, "html.parser")

    # credits_tables = soup.find_all("table", {"class": "simpleCreditsTable"})

    # director = credits_tables[0].find("a")
    # director_url = MAIN_URL + director.get("href")
    # director = director.text.strip()

    cast_list = soup.find("table", {"class": "cast_list"}).find_all("tr")
    cast = []
    for elem in cast_list:
        a = elem.find_all("a")

        if len(a) < 3:
            continue

        name = a[1]
        character = a[2]
        cast_id = name.get("href").split("?")[0].split("/name/")[1][:-1]
        cur_cast = {"nconst": str(cast_id), "character": character.text.strip()}
        cast.append(cur_cast)

    return cast


def scrap_movie_from_suggestions(suggestions, idx):
    """Return details dict for the wanted movie from suggestion

    suggestions are found with
    - suggestions = find_movie_from_kerword(q)
    - show_movie_suggestions(suggestions)
    """
    movie_url = suggestions[idx][1]
    credits_url = f"{movie_url}fullcredits"

    data_details = get_movie_details(movie_url)
    data_credits = get_movie_casts(credits_url)

    data = {**data_details, **data_credits}

    return data


def get_movie_job_details(movie_id, category, principals_df, name_df):
    """Get detail of a person from a category into a movie"""
    cols = ["nconst", "primaryName", "birthYear", "deathYear", "primaryProfession"]

    df = principals_df.loc[
        (principals_df.category.values == category)
        & (principals_df.tconst.values == movie_id)
    ]
    df = df.merge(
        name_df.loc[name_df["nconst"].values == df["nconst"].values], on="nconst"
    )
    df = df[cols]

    return df.to_dict(orient="records")


def get_movie_data(movie_id, movie_cast_url, name_df, basics_df, principals_df):
    """Returns movie informations:

    - 'tconst': id of the movie
    - 'primaryTitle': title of the movie
    - 'startYear': year of the movie
    - 'runtimeMinutes': duration
    - 'director': list of dict of the of directors (mostly 1 element)
    - 'producer': list of dict of the of producers (mostly 1 element)
    - 'cast': list of dict of the of actress and actors
    """
    # get id of the casting
    movie_cast = get_movie_casts(movie_cast_url)

    # Get basic informations of the movie
    movie_data = basics_df.loc[basics_df["tconst"].values == movie_id].to_dict(
        orient="records"
    )[0]
    movie_data["director"] = get_movie_job_details(
        movie_id, "director", principals_df, name_df
    )
    movie_data["producer"] = get_movie_job_details(
        movie_id, "producer", principals_df, name_df
    )

    # Get cast characters details
    movie_cast_df = pd.DataFrame(movie_cast).merge(name_df, on="nconst", how="left")
    movie_data["cast"] = movie_cast_df.to_dict(orient="records")

    return movie_data
