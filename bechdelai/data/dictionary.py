"""Functions for dictionary scraping
from https://www.dictionary.com website
"""
import json
import re

import requests
from bs4 import BeautifulSoup

from bechdelai.data.scrap import get_data_from_url

BASE_URL = "https://www.dictionary.com"
LIST_URL = f"{BASE_URL}/list/{{letter}}/{{num}}"
WORD_URL = f"{BASE_URL}/browse"


# https://www.lexico.com/synonyms/person
person_syn = {
    "person",
    "human being",
    "individual",
    "man",
    "woman",
    "human",
    "being",
    "living soul",
    "girl",
    "boy",
}


def def_with_person_syn(definition):
    """Returns whether the definition starts with
    a or an and a synonym of person
    """
    words_syn = "|".join(person_syn)
    pattern = f"^(?:a|an) ({words_syn})"

    return bool(re.match(pattern, definition))


def filter_noun_def(word_def):
    return {k: v for k, v in word_def.items() if "noun" in k.lower()}


def get_definition_from_word_url(url):
    """Returns the definitions of a word given the
    dictionary word url
    """
    ans = requests.get(url)
    soup = BeautifulSoup(ans.text, "html.parser")

    sections = soup.find("div", {"class": "e16867sm0"}).find_all(
        "section", {"class": "e1hk9ate4"}
    )

    word_res = {}

    for section in sections:
        div = section.find_all("div")
        word_type = div[0].find("span", {"class": ["luna-pos", "pos"]})

        if word_type is None:
            word_type = "none"
        else:
            word_type = word_type.text

        definitions = div[1].find_all("div")
        definitions = filter(lambda x: x.has_attr("value"), definitions)
        definitions = list(map(lambda x: x.text.strip(), definitions))

        word_res[word_type] = definitions

    # filter only on noun def
    word_res = filter_noun_def(word_res)

    # Keep only def with person synonym in
    for k, def_vals in word_res.items():
        def_vals_ = []
        for val in def_vals:
            val_ = set(val.lower().split())
            if len(person_syn.intersection(val_)) > 0:
                def_vals_.append(val)

        word_res[k] = def_vals_

    # remove empty def
    word_res = {k: v for k, v in word_res.items() if len(v) > 0}

    return word_res


def get_url_from_word(word):
    """Find dictionary url from a wanted word"""
    word = word.lower().strip()
    url = f"{WORD_URL}/{word}"

    ans = get_data_from_url(url)

    if ans.url == url:
        return ans

    soup = BeautifulSoup(ans.text, "html.parser")

    sugg = soup.find("h2", {"class": "spell-suggestions-subtitle"})
    sugg = sugg.find("a").text

    url = f"{WORD_URL}/{sugg}"

    return url


def find_words_url(ans):
    """Get url for words in result page"""
    soup = BeautifulSoup(ans.text, "html.parser")

    words_html = soup.find("ul", {"data-testid": "list-az-results"}).find_all("li")
    words = list(map(lambda x: x.find("a"), words_html))
    words_url = {w.text.strip().lower(): w.get("href") for w in words}

    return words_url
