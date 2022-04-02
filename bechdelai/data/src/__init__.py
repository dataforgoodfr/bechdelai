"""Functions to load src files
"""
import json
from os.path import abspath
from os.path import dirname


def load_allocine_filters():
    """Loads allocine filters JSON file"""
    fpath = dirname(abspath(__file__))
    fpath = f"{fpath}/allocine_filters.json"

    with open(fpath, "r", encoding="utf-8") as f:
        res = json.load(f)

    return res
