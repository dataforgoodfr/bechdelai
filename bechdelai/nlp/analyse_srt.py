"""Srt analysis functions"""
import pandas as pd
from pysrt.srttime import SubRipTime

from bechdelai.nlp.entities import extract_keyword
from bechdelai.nlp.entities import remove_not_person_nouns_and_add_gender


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
