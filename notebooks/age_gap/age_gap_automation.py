import sys
sys.path.append("..\..")
import bechdelai.data.wikipedia as wiki
import outputformat as ouf
import pandas as pd
import requests
import io
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy.matcher import PhraseMatcher
from pathlib import Path


class Movie:
    def __init__(self, title):
        self.title = title
        self.plot = self.get_plot(title)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Film : {}".format(self.title)

    @staticmethod
    def get_plot(title):
        return wiki.get_section_text(title, ['Plot'])['Plot']  # to improve


def main():
    hp4 = Movie("Harry Potter 4")
    print(hp4.plot)


if __name__ == "__main__":
    main()
