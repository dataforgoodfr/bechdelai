import zipfile
from io import BytesIO
from typing import Dict
from typing import List

import chardet
import pysrt
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.opensubtitles.org"
QUERY_URL = (
    f"{BASE_URL}/en/search2/sublanguageid-{{language_code}}/moviename-{{movie_name}}"
)

DEFAULT_LANGUAGE_CODE = "fre"


def search(
    movie_name: str, language_code: str = DEFAULT_LANGUAGE_CODE
) -> Dict[str, str]:
    """Search for a movie by name and language and return the url results

    Args:
        movie_name (str): the name of the movie to search for
        language_code (str, optional): the language code to search for. Defaults to DEFAULT_LANGUAGE_CODE.

    Returns:
        Dict[str, str]: dict with movie name and search url
    """
    query_url = QUERY_URL.format(language_code=language_code, movie_name=movie_name)
    try:
        response = requests.get(query_url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        raise Exception("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        raise Exception("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        raise Exception("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        raise Exception("OOps: Something Else", err)

    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("a", {"class": "bnone"})
    if not results:
        return {}
    return {
        result.get_text().replace("\n", " "): f"{BASE_URL}{result.get('href')}"
        for result in results
    }


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
        raise Exception("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        raise Exception("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        raise Exception("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        raise Exception("OOps: Something Else", err)

    soup = BeautifulSoup(response.text, "html.parser")
    download_link = soup.select_one("a[href*=subtitleserve]")
    if not download_link:
        return ""
    return f"{BASE_URL}{download_link.get('href')}"


def download_subtitle_from_url(url: str) -> List[str]:
    response = requests.get(url)
    f = BytesIO()
    f.write(response.content)
    return _extract_zip(f)


def get_subtitles_from_movie(
    movie_name: str,
    language_code: str = DEFAULT_LANGUAGE_CODE,
    search_result_index: int = None,
) -> List[str]:
    """Pipeline to download subtitles with a movie name as input

    Args:
        movie_name (str): the name of the movie to search for
        language_code (str, optional): the language code to search for. Defaults to DEFAULT_LANGUAGE_CODE.
        search_result_index (int, optional):
            the index of the search result to use. Defaults to None.
            if None then suggest result one by one with input

    Returns:
        List[str]: the subtitles from the movie
    """
    search_url = search(movie_name, language_code)
    if not search_url:
        return []

    movie_names = list(search_url.keys())

    # If user want to choose then display movie name one by one
    if search_result_index is None:
        ans = ""
        i = -1
        while ans.lower() != "y":
            i += 1
            if len(movie_names) == i:
                print("No more movies")
                return []

            print(f"Suggestion num {i}: '{movie_names[i]}'")
            print(f"url: {search_url[movie_names[i]]}")
            ans = input("Do you want to get subtitles from this movie ?")
            print()

        movie = movie_names[i]

    else:
        movie = movie_names[search_result_index]

    print(f"Retrieve subtitles for '{movie}'")

    subtitle_url = get_subtitle_link(search_url[movie])
    if not subtitle_url:
        print("No url for subtitles found")
        return []
    return download_subtitle_from_url(subtitle_url)


def _extract_zip(input_zip: BytesIO) -> pysrt.SubRipFile:
    """extract content from zip file

    Args:
        input_zip (BytesIO): the zip file to extract content from

    Returns:
        pysrt.SubRipFile: the extracted content as a pysrt SubRipFile
    """
    try:
        with zipfile.ZipFile(input_zip) as zfile:
            for name in zfile.namelist():
                # If not srt file then continue
                if ".srt" not in name:
                    continue

                # If srt file then get the string
                with zfile.open(name) as readfile:
                    srt = readfile.read()
                    encoding = chardet.detect(srt)["encoding"]
                    srt = srt.decode(encoding)
                    break
    except Exception as e:
        print("Error during unzipping:", e)

    try:
        return pysrt.SubRipFile.from_string(srt, eol="\r\n")
    except Exception as e:
        print("Error during pysrt parsing:", e)

        return pysrt.SubRipFile()
