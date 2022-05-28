import os
import pandas as pd
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
import re 
from ipywidgets import widgets, interact

# Deep Face
from deepface import DeepFace
from deepface.basemodels import VGGFace, OpenFace, Facenet, FbDeepFace
from deepface.commons import functions
# https://github.com/serengil/deepface/blob/master/tests/face-recognition-how.py


def natural_sort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

# Custom imports
from .face_detection import FaceDetector
from .image import Image
from ..utils.video import extract_frames_from_videos

class Video:
    def __init__(self,frames = None,path = None,frame_rate = 5,max_seconds = None):
        
        if path is not None:
            if os.path.isdir(path):
                paths = natural_sort(os.listdir(path))
                self.frames = [Image(os.path.join(path,x)) for x in paths]
            else:
                frames = extract_frames_from_videos(path,frame_rate = frame_rate,save = False,max_seconds = max_seconds)
                self.frames = [Image(img = x) for x in frames]

        else:
            self.frames = frames


    def resize(self,*args,**kwargs):
        for i in tqdm(range(len(self.frames))):
            self.frames[i].resize(*args,**kwargs)

    def extract_faces(self,detector = None,scale_factor = 1.3,min_neighbors = 5,face_size = (100,100),deepface_check = True,deepface_backend = "opencv"):

        if detector is None:
            detector = FaceDetector()

        self.faces = []
        self.faces_metadata = []

        for i,frame in enumerate(tqdm(self.frames)):
            faces = frame.extract_faces(detector,scale_factor = scale_factor,min_neighbors = min_neighbors)
            
            for j,face in enumerate(faces):

                face.resize(size = face_size)

                if deepface_check:
                    try:
                        DeepFace.detectFace(face.array,enforce_detection = True)
                    except:
                        continue

                self.faces.append(face)
                self.faces_metadata.append({"frame_id":i,"face_id":j})

        self.faces_metadata = pd.DataFrame(self.faces_metadata)


    def show_all_faces(self,columns = 10,figsize_row = (8,1)):

        rows = (len(self.faces) // columns) + 1

        for row in range(rows):
            fig = plt.figure(figsize=figsize_row)
            remaining_columns = len(self.faces) - (row * columns)
            row_columns = columns if remaining_columns > columns else remaining_columns
            for column in range(row_columns):
                img = self.faces[row * columns + column].array
                fig.add_subplot(1, columns, column+1)
                plt.axis('off')
                plt.imshow(img)
            plt.show()


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


    def make_faces_tensor(self,input_shape = (224,224),enforce_detection = False):
        faces_array = []
        for face in self.faces:
            face_array = functions.preprocess_face(face.array,input_shape,enforce_detection = False)
            faces_array.append(face_array)
        faces_array = np.concatenate(faces_array,axis = 0)
        return faces_array

    def make_faces_embeddings(self):

        self.model = VGGFace.loadModel()
        input_shape = model.layers[0].input_shape[0][1:3]

        faces_tensor = self.make_faces_tensor(input_shape = input_shape)

        embeddings = self.model.predict(faces_tensor)
        return embeddings


    def replay(self,interval=0.5):

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
            return self.frames[i]

        display(slider)