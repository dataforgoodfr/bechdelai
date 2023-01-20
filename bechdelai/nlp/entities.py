from itertools import permutations
from string import punctuation

import numpy as np
import pandas as pd
import spacy
from flair.data import Sentence
from flair.models import SequenceTagger

from bechdelai.nlp.dictionary import person_syn_dict


with open("../../../data/nlp/stop_words_english.txt", "r", encoding="utf-8") as f:
    stopwords = set(f.read().split("\n"))


# load the NER tagger
tagger = SequenceTagger.load("ner")

# Load neuralcoref model
nlp = spacy.load("en_core_web_sm")


def merge_if_in(elements):
    """Merge elements if start and end intersects"""
    delete_i = []
    for i, j in permutations(range(len(elements)), 2):
        if i in delete_i:
            continue
        e1 = elements[i]
        e2 = elements[j]

        start1, end1 = e1[1], e1[2]
        start2, end2 = e2[1], e2[2]

        if (start1 <= start2 <= end1) & (start1 <= end2 <= end1):
            delete_i.append(j)

    return [e for (i, e) in enumerate(elements) if i not in delete_i]


def remove_not_person_nouns_and_add_gender(ent_list: list) -> list:

    new_ent_list = []
    for ent in ent_list:
        ent_ = extract_person_entity(ent)

        if ent_:
            ent = (*ent, ent_["gender"])
            new_ent_list.append(ent)

    return new_ent_list


def extract_keyword(txt):
    """Extract wanted entities"""
    txt = txt.replace("\n", " ").replace("\t", " ")

    # make a sentence
    sentence = Sentence(txt)

    # run NER over sentence
    tagger.predict(sentence)

    # Run spacy en + neuralcoref
    doc = nlp(txt)

    vocab = list(
        map(
            lambda x: (x.text, x.i, x.i + 1, x.pos_),
            doc,
        )
    )
    vocab = list(
        filter(
            lambda x: x[3] in ["NOUN", "PRON", "PROPN"],
            vocab
            # lambda x: x[3] in ["PRON", "PROPN"], vocab
        )
    )
    entities = list(
        filter(lambda x: x.tag in ["PER", "MISC"], sentence.get_spans("ner"))
    )
    entities = [
        (e.text, e.tokens[0].idx - 1, e.tokens[-1].idx, e.tag) for e in entities
    ]
    entities += vocab
    entities = merge_if_in(entities)

    return entities


def word_is_synonym_of_person(txt, person_syn_dict):
    """If contains a word that match to a person then
    returns the word else return False
    """
    for s in txt.split():
        if s.lower() in person_syn_dict:
            return s.lower()

    return False


def extract_person_entity(entity):
    """Given an entity extracted from `extract_keyword`
    only keep word corresponding to people

    If NOUN then check if the word definition match a person
    Else keep it as such
    """
    ent_ = {}

    if entity[3] == "NOUN":
        w = word_is_synonym_of_person(entity[0], person_syn_dict)
        if w:
            gender = person_syn_dict[w]["gender"]
            ent_["entity"] = entity[0]
            ent_["gender"] = gender

    elif entity[3] == "PRON":
        if entity[0].lower() in ["he", "him", "his", "himself"]:
            ent_["entity"] = entity[0]
            ent_["gender"] = "man"

        elif entity[0].lower() in ["she", "her", "hers", "herself"]:
            ent_["entity"] = entity[0]
            ent_["gender"] = "woman"

        else:
            ent_["entity"] = entity[0]
            ent_["gender"] = "unknown"

    else:
        ent_["entity"] = entity[0]
        ent_["gender"] = "unknown"

    return ent_


def match_one_entity_with_cast(
    txt: str, cast_df: pd.DataFrame, cast_characters: pd.Series
) -> pd.Series:

    # if perfect match then return character and gender found
    if txt in cast_characters:
        return (
            cast_df.loc[cast_characters == txt, ["character", "gender"]]
            .iloc[0]
            .to_frame()
            .T
        )

    for c in cast_characters:
        # if entities match any word in character name then return it
        if txt in c.split():
            return (
                cast_df.loc[cast_characters == c, ["character", "gender"]]
                .iloc[0]
                .to_frame()
                .T
            )

    # else return nothing
    return pd.DataFrame([("", "")], columns=["character", "gender"])


def remove_stopwords_and_punctuation(txt: str) -> str:
    txt = [w for w in txt.split() if w not in stopwords]
    return " ".join(txt).translate(str.maketrans("", "", punctuation))


def match_entities_with_cast(
    entities_found: pd.DataFrame, cast_df: pd.DataFrame
) -> pd.DataFrame:

    entities_found_ = entities_found.copy()

    # process entities text, remove stopwords, strip and to lower
    entities_found_["ent"] = entities_found_["ent"].str.lower()
    entities_found_["ent"] = entities_found_["ent"].apply(
        remove_stopwords_and_punctuation
    )
    entities_found_["ent"] = entities_found_["ent"].str.strip()

    # add char and gender columns
    entities_found_["character"] = ""
    entities_found_["gender_"] = ""

    # analyse remaining entities
    _filter = entities_found_.ent != ""

    cast_characters = cast_df.character.str.lower()
    ent_cast = entities_found_.loc[_filter, "ent"].apply(
        lambda x: match_one_entity_with_cast(x, cast_df, cast_characters)
    )
    ent_cast = pd.concat(ent_cast.values)

    entities_found_.loc[_filter, "character"] = ent_cast.character.values
    entities_found_.loc[_filter, "gender_"] = np.where(
        ent_cast.gender.values == 1,
        "woman",
        np.where(ent_cast.gender.values == 2, "man", ""),
    )

    entities_found["character_found"] = entities_found_.character
    entities_found["gender"] = np.where(
        entities_found_["gender_"] != "",
        entities_found_["gender_"],
        entities_found["gender"],
    )

    return entities_found
