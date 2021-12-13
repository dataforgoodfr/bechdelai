import os
import pandas as pd
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from deepface import DeepFace

from .face_detection import FaceDetector
from .frame import Frame

class Frames:
    def __init__(self,frames = None,path = None):
        
        if path is not None:
            paths = os.listdir(path)
            self.frames = [Frame(os.path.join(path,x)) for x in paths]
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
