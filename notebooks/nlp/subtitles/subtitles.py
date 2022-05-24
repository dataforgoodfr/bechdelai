"""Utils functions"""
import re

import chardet
import pysrt

brackets_pattern = "\[[A-Za-z ]*\]"
parenthesis_pattern = "\([A-Za-z ]*\)"
dash_pattern = r"^-"
html_pattern = "\<.[A-Za-z]*\>"
two_dots_pattern = "^([A-Za-z ]*)\:"

patterns = [
    brackets_pattern,
    parenthesis_pattern,
    dash_pattern,
    html_pattern,
    two_dots_pattern,
]


def load_srt(fpath):
    """Load subtitles form srt file"""
    try:
        srt = pysrt.open(fpath)
    except:
        with open(fpath, "rb") as f:
            encoding = chardet.detect(f.read())["encoding"]

        srt = pysrt.open(fpath, encoding=encoding)

    return srt


def get_dist_between_2_srt(prev, new):
    """Get time distance (in sec) between two subtitles"""
    dist = new - prev
    return round(
        (
            dist.hours * 3600
            + dist.minutes * 60
            + dist.seconds
            + float(f"0.{dist.milliseconds}")
        ),
        3,
    )


def format_srt(srt):
    """Clean srt"""
    srt = srt.split("\n")
    srt_format = []

    for s in srt:
        for p in patterns:
            s = re.sub(p, "", s.strip())

        srt_format.append(s)

    return " ".join(srt_format).strip()
