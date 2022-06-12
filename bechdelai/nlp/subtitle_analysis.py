from typing import Dict, List

import pandas as pd
import spacy
from bechdelai.nlp.utils import (clean_text, compute_gender_spoken_time,
                                 find_entity_groups)
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

    def get_modifiers(self, doc, entities: List[str]) -> Dict[str, List[str]]:
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

            words = []
            for match_id, (target, modifier) in matcher(doc):
                words.append(doc[modifier].text)
            if len(words) > 0:
                modifiers[ent] = words
        return modifiers

    def get_actions(self, doc, entities: List[str]) -> Dict[str, List[str]]:
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

            words = []
            for match_id, (action, target) in matcher(doc):
                words.append(doc[action].lemma_)
            if len(words) > 0:
                actions[ent] = words
        return actions

    def get_passives(self, doc, entities: List[str]) -> Dict[str, List[str]]:
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

            words = []
            for match_id, (action, target) in matcher(doc):
                words.append(doc[action].lemma_)
            if len(words) > 0:
                passives[ent] = words
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
        
        modifiers = self.get_modifiers(doc, entities)
        actions = self.get_actions(doc, entities)
        passives = self.get_passives(doc, entities)
        
        entity_mapping = find_entity_groups(entities)
        
        regrouped_modifiers = {}
        for k, v in modifiers.items():
            regrouped_modifiers.setdefault(entity_mapping.get(k,k),[]).append(modifiers.get(entity_mapping.get(k,k)))
        print("modifiers", regrouped_modifiers)   
         
        regrouped_actions = {}
        for k, v in actions.items():
            regrouped_actions.setdefault(entity_mapping.get(k,k),[]).append(actions.get(entity_mapping.get(k,k)))
        print("actions", regrouped_actions)  
            
        regrouped_passives = {}
        for k, v in passives.items():
            regrouped_passives.setdefault(entity_mapping.get(k,k),[]).append(passives.get(entity_mapping.get(k,k)))
        print("passives", regrouped_passives)

        if segments is not None:
            delta = subtitles[0].start.ordinal / 1000 - segments.loc[0, "start"]
            gender_dialogs = self.segment_dialogs_by_gender(segments, subtitles, delta)
            print(f"{len(gender_dialogs['female'])} dialogs by women i.e {round(100 * len(gender_dialogs['female']) / (len(gender_dialogs['female']) + len(gender_dialogs['male'])))}% of the total")
            
            gender_spoken_time = compute_gender_spoken_time(segments)
            print(f"{round(gender_spoken_time['female'])}s of women talking i.e {round(100 * gender_spoken_time['female'] / (gender_spoken_time['female'] + gender_spoken_time['male']))}% of the total")
