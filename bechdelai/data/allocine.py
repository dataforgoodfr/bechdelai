from bs4 import BeautifulSoup

BASE_URL = "https://www.allocine.fr/"
QUERY_URL = f"{BASE_URL}films/{{genre_filter}}{{pays_filter}}{{decennie_filter}}{{annee_filter}}?page={{page_num}}"

DEFAULT_FILTERS = {
    "genre_filter": "",
    "pays_filter": "",
    "decennie_filter": "",
    "annee_filter": "",
    "page_num": "1",
}


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

    return filters_allocine


def get_allocine_movies_from_one_page(filters: dict):
    filters = {**DEFAULT_FILTERS, **filters}

    for f, v in filters.items():
        if ("filter" in f) and (not v.endswith("/")) and (v != ""):
            filters[f] = f"{v}/"
    print(filters)
    print(filters)
    url = QUERY_URL.format(**filters)

    print(url)
