import numpy as np
from bs4 import BeautifulSoup
from IPython.display import display
from IPython.display import HTML

from bechdelai.data.scrap import get_data_from_url
from bechdelai.data.scrap import RequestException

MAIN_URL = "https://www.imdb.com"
URL_SEARCH = f"{MAIN_URL}/find?s=tt&q={{q}}"


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

    cast_list = soup.find("table", {"class": "cast_list"}).find_all("tr")
    cast = []
    for elem in cast_list:
        a = elem.find_all("a")

        if len(a) < 3:
            continue

        name = a[1]
        character = a[2]
        cast_id = name.get("href").split("?")[0].split("/name/")[1][:-1]

        cur_cast = {
            "nconst": int(
                str(cast_id)[2:]
            ),  # convert id to int (from "nm1234567" to int(1234567))
            "character": character.text.strip(),
        }
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


def _postprocess_one_cast(x):
    """Apply the following
    - format cast id to IMDB format
    - add online url
    - Add gender
    """
    formated_id = "nm" + str(x["nconst"]).zfill(7)
    x["nconst"] = formated_id
    x["url"] = f"{MAIN_URL}/name/{formated_id}/"

    if "actress" in str(x["primaryProfession"]):
        x["gender"] = "F"
    elif "actor" in str(x["primaryProfession"]):
        x["gender"] = "M"
    else:
        x["gender"] = "?"

    return x


def postprocess_cast_id(full_cast):
    """Postprocess Id of casting as IMDB format

    We use integer ID to get a result faster, but
    IMDB use a string format

    1234567 become "nm1234567"
    """
    # apply function for each element
    for i, cast in enumerate(full_cast):
        _postprocess_one_cast(cast)
        cast["ordering"] = i + 1

    return full_cast


def get_movie_job_details(movie_principals, category, name_df):
    """Get detail of a person from a category into a movie

    Requires 3 datasets from IMDB:
    - name_df : https://datasets.imdbws.com/name.basics.tsv.gz

    Parameters
    ----------
    movie_principals: pandas.DataFrame
        Principals dataframe filtered on the wanted movie
    category: str
        Job category (mainly used for "director" and "producer")
    """
    cols = ["nconst", "primaryName", "birthYear", "deathYear", "primaryProfession"]

    df = movie_principals.loc[movie_principals.category.values == category]
    if len(df) == 0:
        return None

    df = df.merge(
        name_df.loc[name_df["nconst"].values == df["nconst"].values], on="nconst"
    )
    df = df[cols]

    res = df.to_dict(orient="records")[0]
    res = _postprocess_one_cast(res)

    return res


def get_movie_data(movie_id, movie_cast_url, name_df, basics_df, principals_df):
    """Returns movie informations:

    - 'tconst': id of the movie
    - 'primaryTitle': title of the movie
    - 'startYear': year of the movie
    - 'runtimeMinutes': duration
    - 'director': director
    - 'producer': producer
    - 'cast': list of dict of the of actress and actors

    Requires 3 datasets from IMDB:
    - name_df : https://datasets.imdbws.com/name.basics.tsv.gz
    - basics_df : https://datasets.imdbws.com/title.basics.tsv.gz
    - principals_df : https://datasets.imdbws.com/title.principals.tsv.gz
    """
    # get id of the casting
    movie_cast = get_movie_casts(movie_cast_url)

    # Get id as int and as imdb format
    if str(movie_id).startswith("tt"):
        movie_id = int(movie_id[2:])

    movie_id_imdb = f"tt{movie_id:07}"

    # Get basic informations of the movie
    movie_data = basics_df.loc[basics_df["tconst"].values == movie_id].to_dict(
        orient="records"
    )[0]
    movie_data["tconst"] = movie_id_imdb
    movie_data["url"] = f"{MAIN_URL}/name/{movie_id_imdb}/"
    movie_principals = principals_df.loc[principals_df.tconst.values == movie_id]

    movie_data["director"] = get_movie_job_details(
        movie_principals, "director", name_df
    )
    movie_data["producer"] = get_movie_job_details(
        movie_principals, "producer", name_df
    )

    # Get cast characters details
    full_cast = []
    for cast in movie_cast:
        cast_id = cast["nconst"]
        idx = np.where(name_df.nconst.values == cast_id)[0][0]
        full_cast.append(name_df.iloc[idx].to_dict())

    movie_data["cast"] = postprocess_cast_id(full_cast)

    return movie_data
