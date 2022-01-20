
from io import BytesIO

import cv2 as cv
import matplotlib.pyplot as plt
import pandas as pd
import requests
import spacy
from PIL import Image
from wikidata.client import Client

wikidata_client = Client()
nlp = spacy.load("fr_core_news_lg")
nlp.add_pipe("opentapioca")



def analyze_text(data, image):
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

                image_url = get_picture_url(entity)
                if image_url:
                    print(image_url)
                    actor_image = get_picture(image_url)
                    

    return pd.DataFrame(
        {"Q_id": ids, "Name": names, "gender": genders, "description": descriptions}
    )


def analyze_image(image, faces):
    return


def get_gender_info(entity):
    gender_prop = wikidata_client.get("P21")
    gender = entity[gender_prop]
    return str(gender.label)


def get_picture_url(entity):
    image_prop = wikidata_client.get("P18")
    try:
        image = entity[image_prop]
        return image.image_url
    except KeyError:
        return


def get_picture(url):
    response = requests.get(url)
    output = BytesIO(response.content)
    output.seek(0)
    output.flush()
    try:
        return Image.open(output)
    except:
        return


