"""Srt analysis functions"""
from itertools import permutations

import pandas as pd
import spacy
from flair.data import Sentence
from flair.models import SequenceTagger
from pysrt.srttime import SubRipTime

from bechdelai.nlp.dictionary import person_syn_dict

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


def srt_time_to_sec(srt_time: SubRipTime) -> int:
    """_summary_

    Parameters
    ----------
    srt_time : SubRipTime
        _description_

    Returns
    -------
    int
        _description_
    """
    return int(srt_time.seconds + srt_time.minutes * 60 + srt_time.hours * 3600)


def extract_keyword(txt):
    """Extract wanted entities"""
    # make a sentence
    sentence = Sentence(txt)

    # run NER over sentence
    tagger.predict(sentence)

    # Run spacy en + neuralcoref
    doc = nlp(txt)

    vocab = list(
        map(
            lambda x: (x.text, x.i + 1, x.i + 2, x.pos_),
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


def time_to_sec(t):
    """Convert timestamp to seconds"""
    seconds = (t.hour * 60 + t.minute) * 60 + t.second
    return seconds


def extract_person_entities_from_srt(srt):
    """Extract entities from an srt object and then
    apply `extract_person_entity` on each entity
    """
    ent = extract_keyword(srt.text)

    entities = []
    for e in ent:
        ent_ = extract_person_entity(e)

        if ent_:
            entities.append(ent_)

    if entities:
        return {
            "start_sec": time_to_sec(srt.start.to_time()),
            "end_sec": time_to_sec(srt.end.to_time()),
            "duration": time_to_sec(srt.duration.to_time()),
            "entities": entities,
        }

    return None


def extract_person_references_in_srt(
    srt_list: list, max_idx: int = None
) -> pd.DataFrame:
    """_summary_

    Parameters
    ----------
    srt_list : list
        _description_
    max_idx : int, optional
        _description_, by default None

    Returns
    -------
    pd.DataFrame
        _description_
    """

    if max_idx is not None:
        srt_list = srt_list[:max_idx]

    results = []
    srt_details = []

    for i, srt in enumerate(srt_list):
        res = extract_keyword(srt.text)
        res = remove_not_person_nouns_and_add_gender(res)

        results.extend([(i, *r) for r in res])

        srt_details.append(
            [i, srt.text, srt_time_to_sec(srt.start), srt_time_to_sec(srt.end)]
        )

    results = pd.DataFrame(
        results, columns=["srt_id", "ent", "start_idx", "end_idx", "ent_type", "gender"]
    )
    srt_details = pd.DataFrame(
        srt_details, columns=["srt_id", "text", "start_sec", "end_sec"]
    )

    return srt_details.merge(results, on="srt_id")
