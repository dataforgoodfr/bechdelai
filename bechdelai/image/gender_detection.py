import pandas as pd
from .clip import CLIP


class GenderDetector:
    def __init__(self):

        self.prompts = {"gender":["man","woman"]}
        self.model = CLIP(self.prompts)


    def predict(self,faces,faces_metadata = None,th_unknown = 0.1,th_woman = 0.4):

        _,probas = self.model.predict(faces)

        probas["diff"] = (probas["man"] - probas["woman"]).abs()
        probas["gender"] = probas[["man","woman"]].idxmax(axis = 1)
        probas.loc[probas["diff"] < th_unknown,"gender"] = "unknown"
        probas.loc[(probas["diff"] > th_unknown) & (probas["woman"] > th_woman),"gender"] = "woman"
        # probas.loc[(probas["woman"] > th_woman),"gender"] = "woman"

        if faces_metadata is not None:
            annotations = (
                pd.concat([faces_metadata,probas],axis = 1)
                .groupby(["frame_id","gender"])
                ["face_id"]
                .count()
                .unstack("gender")
                .fillna(0)
                .to_dict(orient = "index")
            )
            return probas,annotations
        else:
            return probas


