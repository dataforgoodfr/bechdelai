import itertools
from typing import Dict, List

import pandas as pd
import textdistance


def _group_entities(entities: List[str]) -> Dict[str, int]:
    """Group entities by their similarity to each other.

    Args:
        entities (List[str]): The entities to group

    Returns:
        Dict[str, int]: The grouped entities
    """
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
    """Reverse the entity mapping.

    Args:
        regrouped_entities (Dict[str, int]): 

    Returns:
        Dict[int, List[str]]: _description_
    """
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
