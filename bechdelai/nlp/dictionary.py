"""Process synonyms dictionary"""
import json
import re

from bechdelai.data.dictionary import person_syn

dict_path = "../../../data/dictionary/syn_person.json"
with open(dict_path, "r") as f:
    person_syn_dict = json.load(f)


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
