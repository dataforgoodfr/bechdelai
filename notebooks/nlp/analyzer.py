import json
import re
from collections import Counter

import pandas as pd
import pysrt
from booknlp.booknlp import BookNLP


class TextAnalyzer:
    def __init__(self):
        model_params = {
            "model": "small",
            "pipeline": "entity,quote,event,coref",
        }
        self.model = BookNLP("en", model_params)

        self.input_file = "data/sub.txt"
        self.output_directory = "data/predictions/"
        self.quotes = pd.DataFrame()
        self.entities = pd.DataFrame()
        self.agent = pd.DataFrame()
        self.patient = pd.DataFrame()
        self.possess = pd.DataFrame()
        self.modifiers = pd.DataFrame()

    def analyze(self, book_id: str, srt_file_path: str):
        subs = self._read_data(srt_file_path)
        self._process_srt(subs)
        self.model.process(self.input_file, self.output_directory, book_id)
        self._read_predictions(book_id)

    def _read_data(self, path: str) -> list:
        return pysrt.open(path)

    def _process_srt(self, subs: list) -> None:
        texts = [self._clean_text(s.text) for s in subs]
        with open(self.input_file, "w", encoding="utf8") as f:
            f.write(" ".join(texts))

    def _clean_text(self, t: str) -> str:
        cleaned = t.replace("\n", " ").replace("  ", " ").replace(" -", " ")
        wo_html = re.sub("<[^<]+?>", "", cleaned)
        wo_parentheses = re.sub(r"\([^()]*\)", "", wo_html)
        return (
            wo_parentheses
            if ":" not in wo_parentheses
            else wo_parentheses.split(":")[1]
        )

    def _read_character_file(self, book_id: str) -> None:
        with open(
            f"{self.output_directory}{book_id}.book", "r", encoding="utf8"
        ) as file:
            data = json.load(file)

        for character in data["characters"]:
            possCounter = Counter()

            agent_list = character["agent"]
            patient_list = character["patient"]
            poss_list = character["poss"]
            mod_list = character["mod"]

            character_id = character["id"]
            count = character["count"]

            referential_gender_distribution = referential_gender_prediction = "unknown"

            if character["g"] is not None and character["g"] != "unknown":
                referential_gender_distribution = character["g"]["inference"]
                referential_gender = character["g"]["argmax"]

            mentions = character["mentions"]
            proper_mentions = mentions["proper"]
            max_proper_mention = ""

            if len(mentions["proper"]) > 0:
                max_proper_mention = mentions["proper"][0]["n"]
                self.agent = pd.concat(
                    [
                        self.agent,
                        pd.DataFrame(
                            {
                                "character_id": character_id,
                                "name": max_proper_mention,
                                "referential_gender": referential_gender,
                                "attr": self._get_counter_from_dependency_list(
                                    agent_list
                                ).keys(),
                                "cnt": self._get_counter_from_dependency_list(
                                    agent_list
                                ).values(),
                            }
                        ),
                    ]
                )
                self.patient = pd.concat(
                    [
                        self.patient,
                        pd.DataFrame(
                            {
                                "character_id": character_id,
                                "name": max_proper_mention,
                                "referential_gender": referential_gender,
                                "attr": self._get_counter_from_dependency_list(
                                    patient_list
                                ).keys(),
                                "cnt": self._get_counter_from_dependency_list(
                                    patient_list
                                ).values(),
                            }
                        ),
                    ]
                )
                self.possess = pd.concat(
                    [
                        self.possess,
                        pd.DataFrame(
                            {
                                "character_id": character_id,
                                "name": max_proper_mention,
                                "referential_gender": referential_gender,
                                "attr": self._get_counter_from_dependency_list(
                                    poss_list
                                ).keys(),
                                "cnt": self._get_counter_from_dependency_list(
                                    poss_list
                                ).values(),
                            }
                        ),
                    ]
                )
                self.modifiers = pd.concat(
                    [
                        self.modifiers,
                        pd.DataFrame(
                            {
                                "character_id": character_id,
                                "name": max_proper_mention,
                                "referential_gender": referential_gender,
                                "attr": self._get_counter_from_dependency_list(
                                    mod_list
                                ).keys(),
                                "cnt": self._get_counter_from_dependency_list(
                                    mod_list
                                ).values(),
                            }
                        ),
                    ]
                )

    def _read_predictions(self, book_id: str):
        self.quotes = pd.read_csv(f"{self.output_directory}{book_id}.quotes", sep="\t")
        self.entities = pd.read_csv(
            f"{self.output_directory}{book_id}.entities", sep="\t"
        )
        self._read_character_file(book_id)

    def _get_counter_from_dependency_list(self, dep_list: list):
        counter = Counter()
        for token in dep_list:
            term = token["w"]
            tokenGlobalIndex = token["i"]
            counter[term] += 1
        return counter


if __name__ == "__main__":
    analyzer = TextAnalyzer()
    analyzer.analyze(
        "encanto",
        "./data/raw/open-subtitles/Encanto.2021.1080p.WEB-DL.H264.DDP5.1-EVO.srt",
    )
    analyzer.quotes.to_csv("quotes.csv")
    analyzer.entities.to_csv("entities.csv")
    analyzer.agent.to_csv("agent.csv")
    analyzer.patient.to_csv("patient.csv")
    analyzer.possess.to_csv("poss.csv")
    analyzer.modifiers.to_csv("mod.csv")
