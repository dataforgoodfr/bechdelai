"""Process synonyms dictionary"""
import re

from bechdelai.data.dictionary import person_syn
from bechdelai.processing.analyse_srt import extract_keyword
from bechdelai.processing.analyse_srt import word_is_synonym_of_person


def def_with_person_syn(definition):
    """Returns whether the definition starts with
    a or an and a synonym of person
    """
    words_syn = "|".join(person_syn)
    pattern = f"^(a|an)((\s)|(\s[a-zA-Z]*\s))({words_syn})"

    return bool(re.match(pattern, definition))


def find_word_gender(definition):
    """Returns the gender based on the definition"""
    woman_pat = "^a (girl|woman)"
    man_pat = "^a (boy|man)"

    if re.match(woman_pat, definition):
        return "woman"
    elif re.match(man_pat, definition):
        return "man"
    else:
        return "unknown"


# TODO process plural words
def process_syn_dict(person_syn_dict):
    """Process a dictionary to only keep word (stored in keys)
    that are synonyms with 'person'

    The condition is contained in this function `def_with_person_syn`
    """
    person_syn_dict = {
        k: v
        for k, v in person_syn_dict.items()
        if def_with_person_syn(list(v["def"].values())[0][0])
    }

    for k, v in person_syn_dict.items():
        def_ = list(v["def"].values())[0][0]

        person_syn_dict[k]["gender"] = find_word_gender(def_)

    return person_syn_dict


def time_to_sec(t):
    """Convert timestamp to seconds"""
    seconds = (t.hour * 60 + t.minute) * 60 + t.second
    return seconds


def extract_person_entity(entity, person_syn_dict):
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


def extract_person_entities_from_srt(srt, person_syn_dict):
    """Extract entities from an srt object and then
    apply `extract_person_entity` on each entity
    """
    ent = extract_keyword(srt.text)

    entities = []
    for e in ent:
        ent_ = extract_person_entity(e, person_syn_dict)

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
