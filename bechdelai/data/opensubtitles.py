import zipfile
from io import BytesIO, TextIOWrapper

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.opensubtitles.org"
QUERY_URL = (
    f"{BASE_URL}/en/search2/sublanguageid-{{language_code}}/moviename-{{movie_name}}"
)

DEFAULT_LANGUAGE_CODE = "fre"


def search(movie_name: str, language_code: str = DEFAULT_LANGUAGE_CODE) -> str:
    """Search for a movie by name and language and return the first search url result

    Args:
        movie_name (str): the name of the movie to search for
        language_code (str, optional): the language code to search for. Defaults to DEFAULT_LANGUAGE_CODE.

    Returns:
        str: first search url result
    """
    query_url = QUERY_URL.format(language_code=language_code, movie_name=movie_name)
    try:
        response = requests.get(query_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)

    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("a", {"class": "bnone"})
    if not results:
        return ""
    return f"{BASE_URL}{results[0].get('href')}"


def get_subtitle_link(search_url: str) -> str:
    """Get the first subtitle link from the search url

    Args:
        search_url (str): the search url to get the subtitle link from

    Returns:
        str: the subtitle download link from the search url
    """
    try:
        response = requests.get(search_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)

    soup = BeautifulSoup(response.text, "html.parser")
    download_link = soup.select_one("a[href*=subtitleserve]")
    if not download_link:
        return ""
    return f"{BASE_URL}{download_link.get('href')}"


def download_subtitle_from_url(url: str) -> list[str]:
    response = requests.get(url)
    f = BytesIO()
    f.write(response.content)
    return _extract_zip(f)


def get_subtitles_from_movie(
    movie_name: str, language_code: str = DEFAULT_LANGUAGE_CODE
) -> list[str]:
    """Pipeline to download subtitles with a movie name as input

    Args:
        movie_name (str): the name of the movie to search for
        language_code (str, optional): the language code to search for. Defaults to DEFAULT_LANGUAGE_CODE.

    Returns:
        list[str]: the subtitles from the movie
    """
    search_url = search(movie_name, language_code)
    if not search_url:
        return []
    subtitle_url = get_subtitle_link(search_url)
    if not subtitle_url:
        return []
    return download_subtitle_from_url(subtitle_url)


def _extract_zip(input_zip: BytesIO) -> list[str]:
    """extract content from zip file

    Args:
        input_zip (BytesIO): the zip file to extract content from

    Returns:
        list[str]: the extracted content
    """
    subtitles = []
    with zipfile.ZipFile(input_zip) as zfile:
        for name in zfile.namelist():
            with zfile.open(name) as readfile:
                for line in TextIOWrapper(readfile, "ISO-8859-1"):
                    subtitles.append(line)
    return subtitles
