import os
from dotenv import load_dotenv
from inaSpeechSegmenter import Segmenter
# import streamlit as st
import pandas as pd
# from inaSpeechSegmenter.export_funcs import seg2csv, seg2textgrid


class Movie:
    def __init__(self, path_to_file):
        self.title = path_to_file.split(sep='\\')[-1].split(sep='.')[0]
        self.media = path_to_file
        self.gendered_audio_seg = self.segment()  # Dataframe
        self.dialogues = None

    def __str__(self):
        return "Film : {}".format(self.title)

    def __repr__(self):
        return self.title

    def segment(self):
        seg = Segmenter(vad_engine='sm', energy_ratio=0.05)
        # energy ratio : the higher, the more selective ; vad_engine : works better with sm than smn
        segment = seg(self.media)
        return pd.DataFrame(list(filter(lambda x: x[0] == 'male' or x[0] == 'female', segment)),
                            columns=['gender', 'start', 'end'])

    def search_gender_tag(self, time):  # Give a time in seconds
        gender = None
        if time > self.gendered_audio_seg['end'].tail(1).item():
            return None
        for i in self.gendered_audio_seg.index:
            if time > self.gendered_audio_seg['start'][i]:
                if time < self.gendered_audio_seg['end'][i]:
                    gender = self.gendered_audio_seg['gender'][i]
                if time > self.gendered_audio_seg['end'][i]:
                    pass
        return gender


if __name__ == '__main__':
    load_dotenv()
    path_to_video = os.getenv("path_to_extract", "./")
    movie = Movie(path_to_video)
    gender_of_time_45 = movie.search_gender_tag(45)  # None
    gender_of_time_60 = movie.search_gender_tag(60)  # Male
    gender_of_time_93 = movie.search_gender_tag(93)  # Female
    gender_of_time_399 = movie.search_gender_tag(399)  # None
    print(
        " Second 45 : " + str(gender_of_time_45),
        " Second 60 : " + str(gender_of_time_60),
        " Second 93 : " + str(gender_of_time_93),
        " Second 399 : " + str(gender_of_time_399)
    )
    # # print(*r, sep = '\n')
    # print(len(r))
    # time = st.slider(
    #     "Sélectionner un temps",
    #     0, 400, 1)

    # print('\n'.join(map(str, gendered_segmentation)))
