"""Functions to scrap scripts from IMSDB
"""
import pandas as pd
from bs4 import BeautifulSoup

from bechdelai.data.scrap import get_data_from_url

ALL_URL = "https://imsdb.com/all-scripts.html"
BASE_URL = "https://imsdb.com"


def get_all_scripts():
    """Scrap all scripts from IMSDB

    Returns
    -------
    pd.DataFrame
        dataframe of all available movie scripts
        from IMSDB (title and url)
    """

    # Get all scripts from ALL_URL
    ans = get_data_from_url(ALL_URL)
    soup = BeautifulSoup(ans.text, "html.parser")

    # All scripts are stored into <p>
    scripts_html = soup.find_all("p")
    meta_list = []

    # Retrieve title and url for each movie
    for html in scripts_html:
        a = html.find("a")
        title = a.text
        title_format = a.get("href").split("/")[-1][:-12]
        title_format = title_format.replace(" ", "-")
        url = f"{BASE_URL}/scripts/{title_format}.html"

        meta_list.append((title, url))

    # format as DF
    df = pd.DataFrame(meta_list, columns=["title", "url"])

    return df


def get_script_from_url(url):
    """Retrieve script from url

    Parameters
    ----------
    url : str
        Valid url to get the script

    Returns
    -------
    list
        List of lines of the script
    """

    ans = get_data_from_url(url)
    soup = BeautifulSoup(ans.text, "html.parser")

    # Get script and split it as a array by line
    script = soup.find("pre").find("pre").text.split("\n")

    return script
