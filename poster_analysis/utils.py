import spacy
import pandas as pd
import requests
from wikidata.client import Client

wikidata_client = Client()
nlp = spacy.load("fr_core_news_lg")
nlp.add_pipe("opentapioca")


def analyze(data):
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


def get_gender_info(entity):
    gender_prop = wikidata_client.get("P21")
    gender = entity[gender_prop]
    return str(gender.label)


def get_picture_url(entity):
    image_prop = wikidata_client.get("P16")
    image = entity[image_prop]
    return image.image_url
