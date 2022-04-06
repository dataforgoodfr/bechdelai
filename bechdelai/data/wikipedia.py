"""
Functions to get data from wikipedia
"""
import requests
from bs4 import BeautifulSoup
import re
import outputformat as ouf
import wikipediaapi
from bechdelai.data.scrap import get_json_from_url

def get_sections(query, lang="en"):
    """Return all sections and subsections in the page and their corresponding indexes

    Parameters
    ----------
    query : str
        Movie query to research
    lang : str
        Language of Wikipedia to research

    Returns
    -------
    dict
        sections dictionary
        sections and subsections are keys. corresponding indexes are values.
    """

    URL = "https://"+lang+".wikipedia.org/w/api.php"
    PARAMS = {
        "action": "parse",
        "page": query,
        "format": "json",
        "prop":"sections",
        'redirects': 1
    }

    R = requests.get(url=URL, params=PARAMS)
    if page_exists(R.json()):
        DATA = R.json()["parse"]['sections']
        dict_sections = {}
        for d in DATA:
            dict_sections[d['anchor']]=d['index']
        return dict_sections

def get_section(query, section_index, lang="en"):
    """Return the section of index section_index

    Parameters
    ----------
    query : str
        Movie query to research
    section_index : int
        index of the section (or subsection) to parse
    lang : str
        Language of Wikipedia to research

    Returns
    -------
    str
        html resulted from request
    """

    URL = "https://"+lang+".wikipedia.org/w/api.php"
    PARAMS = {
        "action": "parse",
        "page": query,
        "format": "json",
        "section": section_index,
        "contentmodel":"wikitext",
        'redirects': 1
    }

    R =  requests.get(url=URL, params=PARAMS)
    if page_exists(R.json()):
        return R.json()["parse"]["text"]["*"]


def drop_references(soup):
    """Remove references info from soup"""
    for span in soup.find_all('span'):
        try:
            if "mw-ext-cite-error" in span.get("class"):
                span.extract()
        except TypeError:
            continue
    for div in soup.find_all('div'):
        try:
            if "mw-references-wrap" in div.get("class"):
                div.extract()
        except TypeError:
            continue

def drop_img_caption(soup):
    """Remove captions from inner images from soup"""
    for div in soup.find_all('div'):
        try:
            if "thumbcaption" in div.get("class"):
                div.extract()
        except TypeError:
            continue

def remove_cite(text):
    """Remove citations (e.g. [1],[30],etc) from text"""
    return re.sub("\[[0-9]+\]","",text)

def parse_section_content(html):
    """Transform html in readable text

    Parameters
    ----------
    html : str
        string in html format

    Returns
    -------
    str
        text parsed to a readable format
    """
    soup = BeautifulSoup(html, "html.parser")
    drop_references(soup)
    drop_img_caption(soup)
    text = remove_cite(soup.get_text())
    text = text.replace('\n\n\n\n','').replace('\t',' ')
    return text

def get_section_text(query,section_list:list,lang="en",verbose=False):
    """Return the text from section_list,

    Parameters
    ----------
    query : str
        Movie query to research
    section_list : list of str
        list of sections' name to request
    lang : str
        Language of Wikipedia to research

    Returns
    -------
    dict
        dictionary of parsed texts from sections in section_list(keys)
    """
    if type(section_list)!=list:
        section_list = [section_list]

    # get sections and corresponding index in page
    sections = get_sections(query,lang=lang)
    if sections is None:
        if verbose:
            print('Page not found.')
        return {}
    else:
        if verbose:
            ouf.showdict(sections,title="Page sections")

    # get text from each section in section_name
    contents = {}
    for section_name in section_list:
        if section_name not in sections.keys():
            if verbose:
                print('KeyError: {} is not a section in the page'.format(section_name))
            continue
        section_content = get_section(query,sections[section_name],lang=lang)
        contents[section_name] =parse_section_content(section_content).replace(section_name+'[edit]\n','')
    return contents

def get_links(query, lang="en", verbose=False):
    """
    Get a list of all links in wikipedia page

    Parameters
    ----------
    query : str
        Movie query to research
    lang : str
        Language of Wikipedia to research

    Returns
    -------
    list
        list of str of the pages' titles linked in researched page

    """

    URL = "https://"+lang+".wikipedia.org/w/api.php"
    PARAMS = {
                'action': 'query',
                'prop': 'links',
                'titles': query,
                'pllimit': 'max',
                'format':'json',
                'redirects': 1
    }

    R = requests.get(url=URL, params=PARAMS)
    data = R.json()

    if page_exists(data):
        pages = data["query"]["pages"]
        pg_count = 1
        page_links = []

        if verbose:
            print("Page %d" % pg_count)
        for key, val in pages.items():
            for link in val["links"]:
                if verbose:
                    print(link["title"])
                page_links.append(link["title"])

            while "continue" in data:
                plcontinue = data["continue"]["plcontinue"]
                PARAMS["plcontinue"] = plcontinue

                R = requests.get(url=URL, params=PARAMS)
                data = R.json()
                pages = data["query"]["pages"]

                pg_count += 1

                if verbose:
                    print("\nPage %d" % pg_count)
                for key, val in pages.items():
                    for link in val["links"]:
                        print(link["title"])
                        page_links.append(link["title"])

            if verbose:
                print("%d titles found." % len(page_links))
        return page_links
    else:
        return None

def get_categories(query, lang="en"):
    """
    Get a list of all categories of query

    Parameters
    ----------
    query : str
        Movie query to research
    lang : str
        Language of Wikipedia to research

    Returns
    -------
    list
        list of str of the categories

    """
    URL = "https://"+lang+".wikipedia.org/w/api.php"
    PARAMS = {
                'action': 'query',
                'prop': 'categories',
                'titles': query,
                'format':'json',
                'redirects': 1,
                'cllimit':'max'
            }

    R =  requests.get(url=URL, params=PARAMS)

    if page_exists(R.json()):
        pages = R.json()["query"]["pages"]
        categories = []
        for key, val in pages.items():
            for link in val["categories"]:
                categories.append(link["title"])
        return categories
    else:
        return None

def page_exists(request_dict):
    """
    Checks if page exists given the parsed request body

    Parameters
    ----------
    request_dict : dict
        request output after parsing

    Returns
    -------
    bool
        if the page exists

    """
    if 'error' in request_dict: # when using parse
        raise ValueError("This query does not correspond to a Wikipedia page.")
        return False
    elif 'query' in request_dict: # when using query
        page =  request_dict["query"]["pages"]
        pageid = list(page.keys())[0]
        if 'missing' in page[pageid]:
            raise ValueError("This query does not correspond to a Wikipedia page.")
            return False
    return True
