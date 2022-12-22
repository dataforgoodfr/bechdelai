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
from ..image.utils import show_faces_on_image
from .utils import extract_frames_from_video,show_frames
from .utils import extract_frames_from_scenes


def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


class Video:
    def __init__(self,frames = None,path = None,detect_scenes = False,fps = 5,max_seconds = None):
        self._annotations = defaultdict(dict)
        
        if path is not None:
            if os.path.isdir(path):
                paths = natural_sort(os.listdir(path))
                self.frames = [Img(os.path.join(path,x)) for x in paths]
            else:
                if not detect_scenes:
                    cap,frames = extract_frames_from_video(path,fps = fps,save = False,max_seconds = max_seconds,show_progress = True)
                else:
                    cap,frames,scenes = extract_frames_from_scenes(path,show_progress = True)
                    self.scenes = scenes

                self.cap = cap
                self.frames = [Img(img = x) for x in frames]

                if detect_scenes:
                    self.annotate(scenes,"scene")

        else:
            self.frames = frames


    def reset_annotations(self):
        self._annotations = defaultdict(dict)

    @property
    def annotations(self):
        return self._annotations

    @property
    def scenes_durations(self):
        return [x.get_duration() for x in self.scenes]

    def annotate(self,d,key = None):

        if isinstance(d,dict):
            for k,v in d.items():
                assert isinstance(v,dict)
                self._annotations[k].update(v)
        elif isinstance(d,list):
            assert len(d) == len(self.frames)
            assert key is not None
            for i,v in enumerate(d):
                self._annotations[i].update({key:v})



    def resize(self,*args,**kwargs):
        for i in tqdm(range(len(self.frames))):
            self.frames[i].resize(inplace = True,*args,**kwargs)

    def add_rois(self,rois_list,genders = None):
        for i,rois in enumerate(rois_list):
            if len(rois) > 0:
                self.frames[i] = Img(show_faces_on_image(self.frames[i].array,rois))


    def show_frames(self,columns = 6,figsize_row = (15,1),titles = None):
        show_frames(self.frames,columns = columns,figsize_row = figsize_row,titles = titles)

    def replay(self,interval=0.5,with_annotations = True,with_rois = True):

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