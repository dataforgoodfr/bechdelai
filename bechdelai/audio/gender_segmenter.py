import pandas as pd
from abc import ABC, abstractmethod
from inaSpeechSegmenter import Segmenter


class GenderSegmentor(ABC):
    """Abstract Class common to every gender segmentor.
    Convert an audio file to a dataframe of time slots associated with the speaker's gender.
    """
    @abstractmethod
    def segment(self, audio_file):
        pass


class InaSpeechSegmentor(GenderSegmentor):
    def __init__(self):
        self.seg = Segmenter(vad_engine='sm', energy_ratio=0.05)
        # The higher the energy ratio, the more selective it is ; vad_engine works better with sm than smn

    def segment(self, audio_file):
        """Extracts time intervals from audio_file, according to the speaker's gender.

        Returns:
            pd.DataFrame: Pandas' DataFrame with 3 columns (gender, start, end) and as many lines as needed.
        """
        segment = self.seg(audio_file)
        return pd.DataFrame(list(filter(lambda x: x[0] == 'male' or x[0] == 'female', segment)),
                            columns=['gender', 'start', 'end'])
