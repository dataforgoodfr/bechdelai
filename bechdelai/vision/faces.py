
import cv2
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from PIL import Image

from retinaface import RetinaFace
from deepface import DeepFace


class FacesDetector:
    def __init__(self):
        pass

    def detect(self,img:np.array,padding = 0):

        rois = RetinaFace.detect_faces(img)

        if padding == 0:
            faces = RetinaFace.extract_faces(img,align = True)
            faces = [Image.fromarray(x[:,:,[2,1,0]]) for x in faces]
        else:
            faces = self.get_rois(img,rois,padding = padding)

        return rois,faces

    def get_rois(self,img:np.array,rois,padding = 0):

        selected_rois = []

        for _,values in rois.items():
            (x1,y1,x2,y2) = values["facial_area"]
            roi = Image.fromarray(img[
                max([y1-padding,0]):min([y2+padding,img.shape[0]]),
                max([x1-padding,0]):min([x2+padding,img.shape[1]])
            ])
            selected_rois.append(roi)
        
        return selected_rois



    def show_faces_on_image(self,img,rois,width = 2,color = (255,0,0)):

        new_img = np.copy(img)

        for _,values in rois.items():
            (x1,y1,x2,y2) = values["facial_area"]
            cv2.rectangle(new_img,(x1,y1),(x2,y2),color,width)

        new_img = Image.fromarray(new_img)
        return new_img



    def show_all_faces(self,faces,columns = 10,figsize_row = (15,1),titles = None):

        rows = (len(faces) // columns) + 1

        for row in range(rows):
            fig = plt.figure(figsize=figsize_row)
            remaining_columns = len(faces) - (row * columns)
            row_columns = columns if remaining_columns > columns else remaining_columns
            for column in range(row_columns):
                i = row * columns + column
                img = np.array(faces[i])
                fig.add_subplot(1, columns, column+1)
                plt.axis('off')
                plt.imshow(img)
                if titles is not None:
                    plt.title(titles[i])
            plt.show()


    def analyze(self,face,enforce_detection = False):

        if isinstance(face,list):

            faces_data = []

            for f in tqdm(face):
                face_data = self.analyze(f,enforce_detection = enforce_detection)
                faces_data.append(face_data)

            faces_data = pd.DataFrame(faces_data)
            faces_data["title"] = faces_data.apply(lambda x : ", ".join([x['gender'],str(x["age"])]),axis = 1)

            return faces_data

        else:

            if isinstance(face,Image.Image):
                face = np.array(face)

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                face_data = DeepFace.analyze(face,enforce_detection=enforce_detection)
            face_data.pop("emotion")
            face_data.pop("region")
            face_data.pop("race")

            face_data["width"] = face.shape[0]
            face_data["height"] = face.shape[1]
            face_data["area"] = face_data["width"] * face_data["height"]

            return face_data


    def analyze_gender_representation(self,img,padding = 0):

        rois,faces = self.detect(img,padding = padding)
        faces_data = self.analyze(faces)
        faces_data["percentage"] = faces_data["area"] / (img.shape[0]*img.shape[1])
        representation = faces_data.groupby("gender")["percentage"].sum()

        return faces,faces_data,rois,representation

        



        