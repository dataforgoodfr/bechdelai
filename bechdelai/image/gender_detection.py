import pandas as pd
import numpy as np
from PIL import Image
from .clip import CLIP


def get_size(img):

    if isinstance(img,Image.Image):
        return img.size[0] * img.size[1]
    else:
        return img.shape[0] * img.shape[1]


class GenderDetector:
    def __init__(self):

        self.prompts = {"gender":["man","woman"]}
        # Possible to add a prompt "background" to filter out wrong face detection
        self.model = CLIP(self.prompts)


    def predict(self,faces,faces_metadata = None,th_unknown = 0.1,th_woman = 0.4,img = None):

        _,probas = self.model.predict(faces)

        probas["diff"] = (probas["man"] - probas["woman"]).abs()
        probas["gender"] = probas[["man","woman"]].idxmax(axis = 1)
        probas.loc[probas["diff"] < th_unknown,"gender"] = "unknown"
        probas.loc[(probas["diff"] > th_unknown) & (probas["woman"] > th_woman),"gender"] = "woman"
        # probas.loc[(probas["woman"] > th_woman),"gender"] = "woman"

        probas["area"] = [get_size(x) for x in faces]
        probas["area_percentage_relative"] = probas["area"] / probas["area"].sum()
        if img is not None:
            area_img = get_size(img)
            probas["area_percentage_total"] = probas["area"] / area_img

        if faces_metadata is not None:
            annotations_data = (
                pd.concat([faces_metadata,probas],axis = 1)
                .groupby(["frame_id","gender"])
                ["face_id"]
                .count()
                .unstack("gender")
                .fillna(0)
                # .to_dict(orient = "index")
            )
            annotations_dict = annotations_data.to_dict(orient = "index")
            return probas,annotations_data,annotations_dict
        else:
            return probas


    def analyze_probas(self,probas):

        # Prepare and aggregate results
        results = probas.groupby("gender").agg({"area_percentage_relative":"sum","diff":"count"})
        results = results.rename(columns = {"area_percentage_relative":"space_occupied","diff":"count"})

        # Get base KPIs
        woman_count = results.loc["woman","count"]
        man_count = results.loc["man","count"]
        woman_area = results.loc["woman","space_occupied"]
        man_area = results.loc["man","space_occupied"]
        n_characters = results["count"].sum()

        woman_delta = "+" if woman_area > man_area else "-"
        man_delta = "+" if woman_area < man_area else "-"

        if man_area == 0 and woman_area == 0:
            ratio_area = "0% 👩🧑"
        elif man_area == 0:
            ratio_area = "100% 👩"
        elif woman_area == 0:
            ratio_area = "100% 🧑"
        elif woman_area  > man_area:
            ratio_area = f"{round(woman_area/man_area,1)}x 👩"
        else:
            ratio_area = f"{round(man_area/woman_area,1)}x 🧑"

        if man_count == 0 and woman_count == 0:
            ratio_count = "0 👩🧑"
        if man_count == woman_count:
            ratio_count = "👩 = 🧑"
        elif man_count == 0:
            ratio_count = "100% 👩"
        elif woman_count == 0:
            ratio_count = "100% 🧑"
        elif woman_count  > man_count:
            ratio_count = f"{round(woman_count/man_count,1)}x 👩"
        else:
            ratio_count = f"{round(man_count/woman_count,1)}x 🧑"


        metrics = {
            "women_area":woman_area,
            "men_area":man_area,
            "n_women":woman_count,
            "n_men":man_count,
            "ratio_count":ratio_count,
            "ratio_area":ratio_area,
            "n_characters":n_characters,
            "area_gap":woman_area/man_area,
            "count_gap":woman_count/man_count,
        }

        return results,metrics