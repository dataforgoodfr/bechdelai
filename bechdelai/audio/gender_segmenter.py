import pandas as pd
from abc import ABC, abstractmethod
from inaSpeechSegmenter import Segmenter
from inaSpeechSegmenter.segmenter import Gender
from inaSpeechSegmenter.features import media2feats


class GenderSegmentor(ABC):
    """Abstract Class common to every gender segmentor.
    Convert an audio file to a dataframe of time slots associated with the speaker's gender.
    """
    @abstractmethod
    def segment(self, audio_file):
        pass

CONSTANT_INA = 0.02

class InaSpeechSegmentor(GenderSegmentor):
    def __init__(self,only_gender = False,batch_size = 32):
        # The higher the energy ratio, the more selective it is ; vad_engine works better with sm than smn
        if not only_gender:
            self.seg = Segmenter(vad_engine='sm', energy_ratio=0.05)
        else:
            self.gender = Gender(batch_size = batch_size)

    def segment(self, audio_file):
        """Extracts time intervals from audio_file, according to the speaker's gender.

        Returns:
            pd.DataFrame: Pandas' DataFrame with 3 columns (gender, start, end) and as many lines as needed.
        """
        segment = self.seg(audio_file)
        return pd.DataFrame(list(filter(lambda x: x[0] == 'male' or x[0] == 'female', segment)),
                            columns=['gender', 'start', 'end'])

    
    def _convert_whisper_output(self,segments:pd.DataFrame) -> list:
        segments = segments.query("speech").assign(category = lambda x : "speech")[["category","start","end"]]
        convert_to_ina_format = lambda x : int(x/CONSTANT_INA)
        segments["start"] = segments["start"].map(convert_to_ina_format)
        segments["end"] = segments["end"].map(convert_to_ina_format)
        segments = [tuple(x) for x in segments.to_numpy()]
        return segments

    def predict_gender_on_segments(self,audio_file,segments):

        mspec, loge, difflen = media2feats(audio_file, None,0,None,"ffmpeg")
        segments = self.gender(mspec, segments, difflen)

        segments_df = pd.DataFrame(segments,columns = ["gender","start","end"])
        segments_df["start"] = segments_df["start"] * CONSTANT_INA
        segments_df["end"] = segments_df["end"] * CONSTANT_INA
        return segments_df

    



