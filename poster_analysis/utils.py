
from io import BytesIO
from os import makedirs

import pandas as pd
import requests
import spacy
import streamlit as st
from deepface import DeepFace
from icrawler.builtin import GoogleImageCrawler
from PIL import Image
from wikidata.client import Client

wikidata_client = Client()
nlp = spacy.load("fr_core_news_lg")
nlp.add_pipe("opentapioca")



def extract_entities(data):
    blocks = data["blocks"]

    names = []
    descriptions = []
    ids = []
    genders = []

    for block_idx, block in enumerate(blocks):
        block_text = " ".join(
            [word["value"] for line in block["lines"] for word in line["words"]]
        )
        for ent in nlp(block_text.title()).ents:
            if ent.label_ == "PERSON":
                entity = wikidata_client.get(ent.kb_id_, load=True)
                names.append(ent.text.title())
                descriptions.append(ent._.description)
                genders.append(get_gender_info(entity))
                ids.append(ent.kb_id_)

    return pd.DataFrame(
        {"Q_id": ids, "Name": names, "gender": genders, "description": descriptions}
    )


def identify_faces(actor_q_id, actor_name, image):
    dir_path = f'images/{actor_q_id}'
    crawl_image_search(actor_name, dir_path)
    recog_faces(image, dir_path)


def get_gender_info(entity):
    gender_prop = wikidata_client.get("P21")
    try:
        gender = entity[gender_prop]
        return str(gender.label)
    except KeyError:
        return "unknown"


def crawl_image_search(name, dir_path):
    try:
        makedirs(dir_path, exist_ok=False)
        google_Crawler = GoogleImageCrawler(storage = {'root_dir': dir_path}, downloader_threads=4)
        google_Crawler.crawl(keyword = name, max_num = 4)
    except Exception as e:
        print(e)
        return
    
def recog_faces(image, dir_path):
    try:
        best_match = DeepFace.find(image,db_path = dir_path,enforce_detection = True)
        st.write(best_match)
    except Exception as e:
        print(e)
        return
