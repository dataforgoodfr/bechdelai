import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
import re 
from ipywidgets import widgets, interact
from collections import defaultdict

# Custom imports
# from .face_detection import FaceDetector
# from .faces import FacesDetector
from ..image.img import Img
from .frame_extraction import extract_frames_from_videos


def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


class Video:
    def __init__(self,frames = None,path = None,frame_rate = 5,max_seconds = None):
        
        if path is not None:
            if os.path.isdir(path):
                paths = natural_sort(os.listdir(path))
                self.frames = [Img(os.path.join(path,x)) for x in paths]
            else:
                frames = extract_frames_from_videos(path,frame_rate = frame_rate,save = False,max_seconds = max_seconds)
                self.frames = [Img(img = x) for x in frames]

        else:
            self.frames = frames

        self._annotations = defaultdict(dict)

    def reset_annotations(self):
        self._annotations = defaultdict(dict)

    @property
    def annotations(self):
        return self._annotations

    def annotate(self,d):
        for k,v in d.items():
            assert isinstance(v,dict)
            self._annotations[k].update(v)


    def resize(self,*args,**kwargs):
        for i in tqdm(range(len(self.frames))):
            self.frames[i].resize(inplace = True,*args,**kwargs)


    def show_frames(self,columns = 6,figsize_row = (15,1)):

        rows = (len(self.frames) // columns) + 1

        for row in range(rows):
            fig = plt.figure(figsize=figsize_row)
            remaining_columns = len(self.frames) - (row * columns)
            row_columns = columns if remaining_columns > columns else remaining_columns
            for column in range(row_columns):
                img = self.frames[row * columns + column].array
                fig.add_subplot(1, columns, column+1)
                plt.axis('off')
                plt.imshow(img)
            plt.show()

    def replay(self,interval=0.5,with_annotations = True):

        # Prepare widgets
        play = widgets.Play(
            value=0,
            min=0,
            max=len(self.frames) - 1,
            step=1,
            interval=interval * 1000,
            description="Press play",
            disabled=False,
        )

        slider = widgets.IntSlider(min=0, value=0, max=len(self.frames) - 1, step=1)
        widgets.jslink((play, "value"), (slider, "value"))

        # Visualize frames and widgets
        @interact(i=play)
        def show(i):
            if with_annotations:
                print(self.annotations[i])
            return self.frames[i]

        display(slider)