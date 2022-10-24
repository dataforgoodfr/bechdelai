
import cv2
import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from PIL import Image

from retinaface import RetinaFace
from deepface import DeepFace
from deepface.commons import functions

FACE_CASCADE_PATH = "haarcascade_frontalface_default.xml"

class FacesDetector:
    def __init__(self,backend = "retinaface"):

        assert backend in ["retinaface","opencv","hybrid"]
        self.backend = backend

        # Prepare model for OpenCV backend
        if self.backend in ["opencv","hybrid"]:
            self.cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades,FACE_CASCADE_PATH))


    def detect(self,img:np.array,padding = 0,scale_factor = 1.3,min_neighbors = 5,method = None):

        if method is None:
            method = self.backend

        if method == "retinaface":

            rois = RetinaFace.detect_faces(img)
            if not isinstance(rois,dict):
                return {},[]

            if padding == 0:
                faces = RetinaFace.extract_faces(img,align = True)
                faces = [Image.fromarray(x[:,:,[2,1,0]]) for x in faces]
            else:
                faces = self._get_faces_from_rois(img,rois,padding = padding)

            return rois,faces

        elif method == "opencv":

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            rois = self.cascade.detectMultiScale(gray, scale_factor, min_neighbors)
            rois = self._convert_rois_opencv_to_retinaface(rois)
            faces = self._get_faces_from_rois(img,rois,padding = padding)
            return rois,faces

        elif method == "hybrid":

            rois,faces = self.detect(img,padding,scale_factor = 1.1,min_neighbors = 3,method = "opencv")
            if len(faces) > 0:
                rois,faces = self.detect(img,padding,method = "retinaface")
            return rois,faces
            
    def _convert_rois_opencv_to_retinaface(self,rois):
        new_rois = {}
        for i,(x1,y1,w,h) in enumerate(rois):
            x2 = x1+w
            y2 = y1+h
            new_rois[f"face_{i}"] = {"facial_area":[x1,y1,x2,y2]}
        return new_rois


    def _get_faces_from_rois(self,img:np.array,rois,padding = 0):

        selected_rois = []

        for _,values in rois.items():
            (x1,y1,x2,y2) = values["facial_area"]
            roi = Image.fromarray(img[
                max([y1-padding,0]):min([y2+padding,img.shape[0]]),
                max([x1-padding,0]):min([x2+padding,img.shape[1]])
            ])
            selected_rois.append(roi)
        
        return selected_rois



    def show_faces_on_image(self,img,rois,width = 2,color = (255,0,0),faces_data = None):

        new_img = np.copy(img)

        if not isinstance(color,list):
            color = [color]*len(rois)

        if faces_data is not None:
            color = [(255,0,0) if x == "Man" else (172, 239, 159) for x in faces_data["title"].tolist()]

        if rois is not None:
            for i,values in enumerate(list(rois.values())):
                (x1,y1,x2,y2) = values["facial_area"]
                cv2.rectangle(new_img,(x1,y1),(x2,y2),color[i],width)

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


    def predict_gender(self,face):
        model = DeepFace.build_model('Gender')
        img_224, region = functions.preprocess_face(img = face, target_size = (224, 224), grayscale = False, enforce_detection = False, detector_backend = "opencv", return_region = True)
        gender_prediction = model.predict(img_224)[0,:]
        woman_proba,man_proba = gender_prediction
        index_prediction = np.argmax(gender_prediction)
        if index_prediction == 0:
            gender = "Woman"
            proba = woman_proba
        elif index_prediction == 1:
            gender = "Man"
            proba = man_proba
        data = {"gender":gender,"gender_proba_man":man_proba,"gender_proba_woman":woman_proba,"index":index_prediction,"proba":proba}
        return data

    def analyze(self,face,enforce_detection = False,only_gender = True,progress_streamlit = None):

        if isinstance(face,list):

            faces_data = []

            for i,f in enumerate(tqdm(face)):
                face_data = self.analyze(f,enforce_detection = enforce_detection)
                faces_data.append(face_data)

                if progress_streamlit is not None:
                    progress_streamlit.progress((i+1)/len(face))

            faces_data = pd.DataFrame(faces_data)
            faces_data["title"] = faces_data.apply(lambda x : ", ".join([x['gender']]),axis = 1)
            faces_data["title_proba"] = faces_data.apply(lambda x : f'{x["title"]} ({x["proba"]:.2%})',axis = 1)

            return faces_data

        else:

            if isinstance(face,Image.Image):
                face = np.array(face)

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                if only_gender:
                    face_data = self.predict_gender(face)
                else:
                    face_data = DeepFace.analyze(face,enforce_detection=enforce_detection,prog_bar = False)

            try:
                face_data.pop("emotion")
                face_data.pop("region")
                face_data.pop("race")
            except:
                pass

            face_data["width"] = face.shape[0]
            face_data["height"] = face.shape[1]
            face_data["area"] = face_data["width"] * face_data["height"]

            return face_data


    def predict(self,img,padding = 0,progress_streamlit = None):

        rois,faces = self.detect(img,padding = padding)
        if len(faces) == 0:
            return None,None,None,None
        else:
            faces_data = self.analyze(faces,progress_streamlit = progress_streamlit)
            faces_data["percentage"] = faces_data["area"] / (img.shape[0]*img.shape[1])

            results = faces_data.groupby("gender").agg({"area":"sum","percentage":"sum","title":"count"}).rename(columns = {"title":"count"})
            results["ratio_area"] = results["area"].values / results["area"][::-1].values
            results["ratio_count"] = results["count"].values / results["count"][::-1].values

            return faces,faces_data,rois,results

        



        