"""Srt analysis functions"""
import pandas as pd
from pysrt.srttime import SubRipTime

from bechdelai.nlp.entities import extract_keyword
from bechdelai.nlp.entities import remove_not_person_nouns_and_add_gender


def srt_time_to_sec(srt_time: SubRipTime) -> int:
    """Convert SubRipTime to seconds"""
    return int(srt_time.seconds + srt_time.minutes * 60 + srt_time.hours * 3600)


def extract_person_references_in_srt(srt_list: list) -> pd.DataFrame:
    """Given a list of subtitles (srt file) extract entities that relies to a person

    Parameters
    ----------
    srt_list : list
        List of srt object

    Returns
    -------
    pd.DataFrame
        Dataframe with found entities in each srt text.
        Format of returned dataframe :
        - "srt_id": id of srt (ordered by time)
        - "text": text of srt
        - "start_sec": starting second in subtitle
        - "end_sec": ending second in subtitle
        - "ent": text entity found
        - "start_idx": start index in string
        - "end_idx": ending index in string
        - "ent_type": entity type found
        - "gender": if gender found then "man" or "woman" else "unknown"
    """
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
