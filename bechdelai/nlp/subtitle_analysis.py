from typing import Dict, List

import pandas as pd
import spacy
from bechdelai.nlp.entities import find_entity_groups
from bechdelai.nlp.graph import (coocurrence_graph, pagerank_algorithm,
                                 regrouped_entites_graph, visualize_graph)
from bechdelai.nlp.processing import clean_text, compute_gender_spoken_time
from bechdelai.nlp.topics import tfidf_topic_modeling
from pysrt import SubRipFile
from spacy.matcher import DependencyMatcher


class SubtitleAnalyzer:
    def __init__(self, language="en"):
        self.language = language
        if language == "en":
            self.nlp = spacy.load("en_core_web_lg")
        elif language == "fr":
            self.nlp = spacy.load("fr_dep_news_trf")
        else:
            raise Exception("Language not supported")
        self.nlp.add_pipe("merge_entities")

    def get_modifiers(self, doc, entities: List[str], entity_mapping: Dict[str, str]) -> Dict[str, int]:
        """Get the modifiers of the given entities

        Args:
            doc (_type_): The document to analyze
            entities (List[str]): The entities to get the modifiers of

        Returns:
            Dict[str, List[str]]: The modifiers of the given entities
        """
        modifiers = {}
        for ent in entities:
            target = (
                ent.split(" ")[1].lower() if len(ent.split(" ")) > 1 else ent.lower()
            )
            pattern = [
                {"RIGHT_ID": "target", "RIGHT_ATTRS": {"LOWER": target}},
                {
                    "LEFT_ID": "target",
                    "REL_OP": ">>",
                    "RIGHT_ID": "modifier",
                    "RIGHT_ATTRS": {"DEP": {"IN": ["amod", "advmod"]}},
                },
            ]
            matcher = DependencyMatcher(self.nlp.vocab)
            matcher.add(f"Passive_{ent}", [pattern])

            for match_id, (target, modifier) in matcher(doc):
                if doc[target].text in entities:
                    ent = entity_mapping.get(doc[target].text, doc[target].text)
                    k = (ent, doc[modifier].lemma_)
                    if modifiers.get(k) is None:
                        modifiers[k] = 1
                    else:
                        modifiers[k] = modifiers[k] + 1
        return modifiers

    def get_actions(self, doc, entities: List[str], entity_mapping: Dict[str, str]) -> Dict[str, int]:
        """Get the actions of the given entities

        Args:
            doc (_type_): The document to analyze
            entities (List[str]): The entities to get the actions of

        Returns:
            Dict[str, List[str]]: The actions of the given entities
        """
        actions = {}
        for ent in entities:
            target = (
                ent.split(" ")[1].lower() if len(ent.split(" ")) > 1 else ent.lower()
            )
            pattern = [
                {"RIGHT_ID": "action", "RIGHT_ATTRS": {"POS": "VERB"}},
                {
                    "LEFT_ID": "action",
                    "REL_OP": ">>",
                    "RIGHT_ID": "target",
                    "RIGHT_ATTRS": {
                        "DEP": {"IN": ["nsubj", "nsubjpass"]},
                        "LOWER": target,
                    },
                },
            ]
            matcher = DependencyMatcher(self.nlp.vocab)
            matcher.add(f"Passive_{ent}", [pattern])

            for match_id, (action, target) in matcher(doc):
                if doc[target].text in entities:
                    ent = entity_mapping.get(doc[target].text, doc[target].text)
                    k = (ent, doc[action].lemma_)
                    if actions.get(k) is None:
                        actions[k] = 1
                    else:
                        actions[k] = actions[k] + 1
        return actions

    def get_passives(self, doc, entities: List[str], entity_mapping: Dict[str, str]) -> Dict[str, int]:
        """Get the passives of the given entities

        Args:
            doc (_type_): The document to analyze
            entities (List[str]): The entities to get the passives of

        Returns:
            Dict[str, List[str]]: The passives of the given entities
        """
        passives = {}
        for ent in entities:
            target = (
                ent.split(" ")[1].lower() if len(ent.split(" ")) > 1 else ent.lower()
            )
            pattern = [
                {"RIGHT_ID": "action", "RIGHT_ATTRS": {"POS": "VERB"}},
                {
                    "LEFT_ID": "action",
                    "REL_OP": ">>",
                    "RIGHT_ID": "target",
                    "RIGHT_ATTRS": {"DEP": {"IN": ["dobj", "pobj"]}, "LOWER": target},
                },
            ]
            matcher = DependencyMatcher(self.nlp.vocab)
            matcher.add(f"Passive_{ent}", [pattern])

            for match_id, (action, target) in matcher(doc):
                if doc[target].text in entities:
                    ent = entity_mapping.get(doc[target].text, doc[target].text)
                    k = (ent, doc[action].lemma_)
                    if passives.get(k) is None:
                        passives[k] = 1
                    else:
                        passives[k] = passives[k] + 1
        return passives
    

    def segment_dialogs_by_gender(
        self, segments: pd.DataFrame, subtitles: SubRipFile, delta: int = 0
    ) -> Dict[str, List[str]]:
        """Assign dialog lines to a gender from audio segments

        Args:
            segments (pd.DataFrame): audio segments (gender, start, end)
            subtitles (SubRipFile):
            delta (int, optional): Delta between first subtitle and first audio line Defaults to 0.

        Returns:
            Dict[str, List[str]]: The dialog lines of the given gender
        """
        dialogs = {}
        for s in subtitles:
            for i, seg in enumerate(segments.itertuples()):
                if (
                    s.start.ordinal / 1000 - delta > seg.start
                    and s.end.ordinal / 1000 - delta
                    < segments.loc[min(i + 1, len(segments) - 1), "start"]
                ):
                    dialogs.setdefault(seg.gender, []).append(clean_text(s.text))
        return dialogs

    def analyze(self, subtitles: SubRipFile, segments: pd.DataFrame):
        doc = self.nlp(" ".join([clean_text(s.text) for s in subtitles]))
        entities = [
            e.text for e in doc.ents if e.label_ in ["PERSON", "ORG", "GPE", "LOC"]
        ]
        pd.Series(entities).value_counts().nlargest(15).rename('count').to_frame().plot(kind='bar')
        top_entities = pd.Series(entities).value_counts().nlargest(15).index.tolist()
        entity_mapping = find_entity_groups(entities)
        
        modifiers = self.get_modifiers(doc, top_entities, entity_mapping)
        actions = self.get_actions(doc, top_entities, entity_mapping)
        passives = self.get_passives(doc, top_entities, entity_mapping)
        
        coocurrence_G = coocurrence_graph(doc, entity_mapping)
        pagerank_algorithm(coocurrence_G)
        
        modifiers_G = regrouped_entites_graph(modifiers, entity_mapping)
        visualize_graph(modifiers_G, "Modifiers")
         
        actions_G = regrouped_entites_graph(actions, entity_mapping)
        visualize_graph(actions_G, "Actions")
            
        passives_G = regrouped_entites_graph(passives, entity_mapping)
        visualize_graph(passives_G, "Passives")
        
        if segments is not None:
            delta = subtitles[0].start.ordinal / 1000 - segments.loc[0, "start"]
            gender_dialogs = self.segment_dialogs_by_gender(segments, subtitles, delta)
            print(f"{len(gender_dialogs['female'])} lines by women i.e {round(100 * len(gender_dialogs['female']) / (len(gender_dialogs['female']) + len(gender_dialogs['male'])))}% of the total")
            
            gender_spoken_time = compute_gender_spoken_time(segments)
            print(f"{round(gender_spoken_time['female'])} seconds of women talking i.e {round(100 * gender_spoken_time['female'] / (gender_spoken_time['female'] + gender_spoken_time['male']))}% of the total")

            female_tfidf = tfidf_topic_modeling(gender_dialogs["female"])
            male_tfidf = tfidf_topic_modeling(gender_dialogs["male"])
            print("female vocabulary: ", set(female_tfidf).difference(set(male_tfidf)))
            print("male vocabulary: ", set(male_tfidf).difference(set(female_tfidf)))
