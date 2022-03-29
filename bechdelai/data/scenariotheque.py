import pandas as pd
from bechdelai.data.scrap import RequestException, get_data_from_url
from bs4 import BeautifulSoup

MAIN_URL = "https://lecteursanonymes.org/scenario/"


def get_scripts():
    """Return list of scripts available on lecteursanonymes
    with their name and link to download
    """
    url = MAIN_URL

    ans = get_data_from_url(url)

    if ans.status_code != 200:
        raise RequestException(
            "Request response is not valid (status code %s)" % ans.status_code
        )

    df = pd.read_html(url)[0]
    soup = BeautifulSoup(ans.text, "lxml")
    table = soup.find("table")
    links = []
    for tr in table.findAll("tr"):
        trs = tr.findAll("td")
        for each in trs:
            try:
                link = each.find("a")["href"]
                links.append(link)
            except:
                pass
    df["PDF"] = links
    return df

def read_pdf_from_stream(stream):
    """Parse a PDF file
    """
    text = ""
    with fitz.open(stream=stream, filetype="pdf") as doc:
        for page in doc:
            text += page.getText()
    return text
