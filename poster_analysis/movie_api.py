import glob
import os
from io import BytesIO

import cv2
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from icrawler.builtin import GoogleImageCrawler
from PIL import Image

load_dotenv()

headers = {
    "Authorization": f'Bearer {os.getenv("THEMOVIEDB_API_KEY")}',
    "Content-Type": "application/json;charset=utf-8",
}


def search_movie(query: str) -> pd.DataFrame:
    params = {
        "api_key": {os.getenv("THEMOVIEDB_API_KEY")},
        "language": "fr-FR",
        "include_adult": "false",
        "page": 1,
        "query": query,
    }
    response = requests.get(
        f"https://api.themoviedb.org/3/search/movie",
        headers=headers,
        params=params,
    )
    data = response.json()
    return data.get("results")[0]


def get_movie_poster(title: str):
    params = {
        "apikey": {os.getenv("OMDB_API_KEY")},
        "t": title,
    }
    response = requests.get(
        f"http://www.omdbapi.com",
        params=params,
    )
    data = response.json()
    response = requests.get(data.get("Poster"), stream=True)
    poster = Image.open(BytesIO(response.content))
    is_success, im_buf_arr = cv2.imencode(".jpg", np.array(poster))
    byte_im = im_buf_arr.tobytes()
    return byte_im


def download_movie_poster(title: str):
    dir_path = "posters"
    try:
        os.makedirs(dir_path)
        google_crawler = GoogleImageCrawler(
            storage={"root_dir": dir_path}, downloader_threads=3
        )
        filters = dict(size="large")
        google_crawler.crawl(
            keyword=f"{title} official poster", max_num=1, filters=filters
        )
    except Exception as e:
        print(e)
        return
    for fname in glob.glob(f"{dir_path}/*"):
        poster = Image.open(fname)
    is_success, im_buf_arr = cv2.imencode(".jpg", np.array(poster))
    byte_im = im_buf_arr.tobytes()
    return byte_im


def get_movie_credits(movie_id: int) -> pd.DataFrame:
    params = {
        "api_key": {os.getenv("THEMOVIEDB_API_KEY")},
        "language": "fr-FR",
    }
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/credits",
        headers=headers,
        params=params,
    )
    return response.json()
