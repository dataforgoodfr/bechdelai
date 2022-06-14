"""script to scrap words with synonym of person in definition"""
import json
import re
import time

import requests
from bs4 import BeautifulSoup

from bechdelai.data.dictionary import find_words_url
from bechdelai.data.dictionary import get_definition_from_word_url

BASE_URL = "https://www.dictionary.com"
LIST_URL = f"{BASE_URL}/list/{{letter}}/{{num}}"
WORD_URL = f"{BASE_URL}/browse"


def main():
    """Main script to scrap all definition for person synonym"""
    t0 = time.time()
    print("start")
    letters = "abcdefghijklmnopqrstuvwxyz"
    letters = "nopqrstuvwxyz"

    dictionary = {}

    with open("dict.json", "r", encoding="utf-8") as f:
        dictionary = json.load(f)

    start_url = "https://www.dictionary.com/list/n/9"
    url_reached = False

    for letter in letters:
        num = 1
        while True:
            url = LIST_URL.format(letter=letter, num=num)
            if url == start_url:
                url_reached = True

            if not url_reached:
                num += 1
                continue

            ans = requests.get(url)
            print(url, ans.status_code, "---- %.1fs" % (time.time() - t0))

            if ans.status_code != 200:
                break

            words_url = find_words_url(ans)

            for w, word_url in words_url.items():
                # print(w, word_url)
                try:
                    res = get_definition_from_word_url(word_url)
                except Exception as e:
                    print(e)
                    continue

                if not res:
                    continue

                print(w, word_url)

                dictionary[w] = {"url": word_url, "def": res}

            with open("dict.json", "w", encoding="utf-8") as f:
                json.dump(dictionary, f, indent=2)

            num += 1


if __name__ == "__main__":
    main()
