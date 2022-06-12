import itertools
import re
from typing import Dict, List

import pandas as pd
import textdistance


def clean_text(t: str) -> str:
    cleaned = t.replace("\n", " ").replace("  ", " ").replace(" -", " ").replace("♪", "").replace("...", " ").replace("-", "")
    wo_html = re.sub("<[^<]+?>", "", cleaned)
    wo_parentheses = re.sub(r"\([^()]*\)", "", wo_html)
    return (
        wo_parentheses
        if ":" not in wo_parentheses
        else wo_parentheses.split(":")[1]
    )

def _group_entities(entities: List[str]) -> Dict[str, int]:
    regrouped_entities = {}
    i = 0
    for ent_a, ent_b in itertools.combinations(entities, 2):
        if textdistance.jaro_winkler(ent_a, ent_b) > 0.875:
            if regrouped_entities.get(ent_a) is not None and regrouped_entities.get(ent_b) is None:
                regrouped_entities[ent_b] = regrouped_entities.get(ent_a)
            elif regrouped_entities.get(ent_b) is not None and regrouped_entities.get(ent_a) is None:
                regrouped_entities[ent_a] = regrouped_entities.get(ent_b)
            else:
                regrouped_entities[ent_a] = i
                regrouped_entities[ent_b] = i
                i += 1
    return regrouped_entities

def _reverse_entity_mapping(regrouped_entities: Dict[str, int]) -> Dict[int, List[str]]:
    inverse_entities = {}
    for k, v in regrouped_entities.items():
        inverse_entities.setdefault(v,[]).append(k)
    return inverse_entities

def find_entity_groups(entities: List[str]) -> Dict[str, str]:
    regrouped_entities = _group_entities(entities)
    inverse_entities = _reverse_entity_mapping(regrouped_entities) 

    mapping = {}
    for k, v in inverse_entities.items():
        most_used_entity = pd.Series(list(filter(lambda x: x in v, entities))).value_counts().idxmax()
        for ent in v:
            mapping[ent] = most_used_entity
    return mapping

def compute_gender_spoken_time(segments: pd.DataFrame) -> Dict[str, int]:
    spoken_time = {"male": 0, "female": 0}
    for i, seg in enumerate(segments.itertuples()):
        current = spoken_time[seg.gender]
        spoken_time[seg.gender] = current + (seg.end - seg.start)
    return spoken_time

