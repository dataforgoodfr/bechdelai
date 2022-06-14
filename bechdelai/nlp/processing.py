import re
from typing import Dict, List

import pandas as pd


def clean_text(t: str) -> str:
    """Remove noise from text

    Args:
        t (str): text to clean

    Returns:
        str: cleaned tex
    """
    cleaned = t.replace("\n", " ").replace("  ", " ").replace(" -", " ").replace("♪", "").replace("...", " ").replace("-", "")
    wo_html = re.sub("<[^<]+?>", "", cleaned)
    wo_parentheses = re.sub(r"\([^()]*\)", "", wo_html)
    return (
        wo_parentheses
        if ":" not in wo_parentheses
        else wo_parentheses.split(":")[1]
    )

def compute_gender_spoken_time(segments: pd.DataFrame) -> Dict[str, int]:
    """Compute spoken time by gender in audio segments

    Args:
        segments (pd.DataFrame): audio segments

    Returns:
        Dict[str, int]: Spoken time total by gender
    """
    spoken_time = {"male": 0, "female": 0}
    for i, seg in enumerate(segments.itertuples()):
        
        current = spoken_time[seg.gender]
        spoken_time[seg.gender] = current + (seg.end - seg.start)
    return spoken_time

def topic_modeling_processing(nlp, text) -> List[str]:
    """Processing to serve as input to topic modeling

    Args:
        nlp (_type_): Spacy model
        text (_type_): input text

    Returns:
        List[str]: Processed text
    """
    removal= ['ADV','PRON','CCONJ','PUNCT','PART','DET','ADP','SPACE', 'NUM', 'SYM']
    tokens = []
    for summary in nlp.pipe(text):
        proj_tok = [token.lemma_.lower() for token in summary if token.pos_ not in removal and not token.is_stop and token.is_alpha]
        tokens.append(proj_tok)
    return tokens
