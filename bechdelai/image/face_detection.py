
import cv2
import os
import sys
import warnings
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from PIL import Image
from sklearn.cluster import DBSCAN
from umap import UMAP

from retinaface import RetinaFace
from deepface import DeepFace
from deepface.commons import functions
from deepface.detectors import FaceDetector
import mediapipe as mp
from .utils import show_all_faces
from .img import Img

FACE_CASCADE_PATH = "haarcascade_frontalface_default.xml"


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout



class FacesDetector:
    def __init__(self):


        # Prepare model for OpenCV backend
        # if self.backend in ["opencv","hybrid"]:
        self.cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades,FACE_CASCADE_PATH))


    def detect(self,img:np.array,padding = 0,scale_factor = 1.3,min_neighbors = 5,method = "retinaface"):

        assert method in ["retinaface","opencv","ssd","mediapipe","opencv2","mtcnn","fastretinaface","fast"]
        # Faster is SSD 

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

        elif method in ["opencv","ssd","mtcnn"]:
            rois,faces = self._detect_deepface(img,detector_name = method,padding = padding)
            return rois,faces

        elif method == "opencv2":

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            rois = self.cascade.detectMultiScale(gray, scale_factor, min_neighbors)
            rois = self._convert_rois_opencv_to_retinaface(rois)
            faces = self._get_faces_from_rois(img,rois,padding = padding)
            return rois,faces

        elif method == "fastretinaface":

            # First run opencv to avoid running retinaface on picture without any faces
            rois,faces = self.detect(img,padding,scale_factor = 1.1,min_neighbors = 3,method = "opencv2")

            # If you find any faces re-run retinaface on the full picture
            if len(faces) > 0:
                rois,faces = self.detect(img,padding,method = "retinaface")
            return rois,faces

        elif method == "mediapipe":
            rois,faces = self._detect_mediapipe(img,model_selection=1,min_detection_confidence=0.5)
            return rois,faces

        elif method == "fast":

            rois,faces = [],[]

            for method in ["mediapipe","ssd","opencv"]:

                rois_i,faces_i = self.detect(img,method = method)
                rois.extend(rois_i)
                faces.extend(faces_i)

            # TODO remove duplicates 

            return rois,faces

    def _detect_deepface(self,img,detector_name = "ssd",padding = 0):

        assert detector_name in ["opencv","ssd","mtcnn","retinaface"]

        detector = FaceDetector.build_model(detector_name)
        resp = FaceDetector.detect_faces(detector, detector_name, img)

        def reorder(values):
            x1,y1,w,h = values
            return (x1,y1,x1+w,y1+h)
            
        rois = {i:{"facial_area":reorder(x[1])} for i,x in enumerate(resp)}
        faces = self._get_faces_from_rois(img,rois,padding)

        return rois,faces


    def _detect_mediapipe(self,img,model_selection = 1,min_detection_confidence = 0.5,padding = 0):

        mp_face_detection = mp.solutions.face_detection
        mp_drawing = mp.solutions.drawing_utils

        # For static images:
        IMAGE_FILES = []
        with mp_face_detection.FaceDetection(model_selection=model_selection, min_detection_confidence=min_detection_confidence) as face_detection:
            # Convert the BGR image to RGB and process it with MediaPipe Face Detection.
            results = face_detection.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        if results.detections is None:
            return {},[]
        else:
            rois = self._convert_mediapipe_detections_to_rois(results.detections,img)
            faces = self._get_faces_from_rois(img,rois,padding)
            return rois,faces
                

    def _convert_mediapipe_detection_to_roi(self,x,img):
        height,width,_ = img.shape
        x1 = int(x.location_data.relative_bounding_box.xmin * width)
        y1 = int(x.location_data.relative_bounding_box.ymin * height)
        x2 = int((x.location_data.relative_bounding_box.xmin + x.location_data.relative_bounding_box.width)  * width)
        y2 = int((x.location_data.relative_bounding_box.ymin + x.location_data.relative_bounding_box.height)  * height)
        return (x1,y1,x2,y2)

    def _convert_mediapipe_detections_to_rois(self,detections,img):
        rois = {}
        for i,x in enumerate(detections):
            rois[i] = {"facial_area":self._convert_mediapipe_detection_to_roi(x,img)}
        return rois

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

    def show_faces_by_cluster(self, faces, clusters, titles=None, **kwargs):

        for i in range(np.max(clusters)+1):
            print(f"Cluster {i}")
            faces_i = np.array(faces)[list(np.where(clusters == i)[0])]
            if titles is not None:
                titles_i = np.array(titles)[list(np.where(clusters == i)[0])]
                show_all_faces(faces_i, titles=titles_i, **kwargs)
            else:
                show_all_faces(faces_i,  **kwargs)






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


    def predict_many(self,video,padding = 0):
        pass


    def detect_many(self,video,padding = 0,face_size = (100,100),method = "retinaface",**kwargs):

        faces_list = []
        faces_metadata = []
        rois_list = []

        for i,frame in enumerate(tqdm(video.frames)):
            rois,faces = self.detect(frame.array,method = method,padding = padding,**kwargs)
            rois_list.append(rois)
            
            for j,face in enumerate(faces):
                # face = face.resize(size = face_size)
                faces_list.append(face)
                faces_metadata.append({"frame_id":i,"face_id":j})

        faces_metadata = pd.DataFrame(faces_metadata)
        return faces_list,faces_metadata,rois_list
        

    def make_embeddings(self,faces_array):
        embeddings = self.model.predict(faces_array)
        return embeddings


    def reduce_embeddings(self,embeddings,n_components = 2,**kwargs):
        self.reducer = UMAP(n_components = n_components,**kwargs)
        embeddings = self.reducer.fit_transform(embeddings)
        embeddings = pd.DataFrame(embeddings,columns = ["x","y"])
        return embeddings


    def cluster_embeddings(self,embeddings,method = "dbscan",**kwargs):

        self.clustering_model = DBSCAN(**kwargs)
        clusters = self.clustering_model.fit_predict(embeddings)
        embeddings["cluster"] = clusters
        embeddings["cluster"] = embeddings["cluster"].astype(str)
        return embeddings,clusters


    def show_embeddings2D(self,embeddings2D,faces = None,size = 0.5,opacity = 0.8):

        # Plot scatter plot

        if "cluster" in embeddings2D.columns:
            fig = px.scatter(
                embeddings2D.assign(size = lambda x : 20),
                x="x",
                y="y",
                color="cluster",
                size = "size"
            )
        else:
            fig = px.scatter(
                embeddings2D,
                x="x",
                y="y",
            )

        # Add faces
        if faces is not None:

            for i, face in enumerate(faces):
                row = embeddings2D.iloc[i]
                fig.add_layout_image(
                    dict(
                        source=face,
                        xref="x",
                        yref="y",
                        xanchor="center",
                        yanchor="middle",
                        x=row["x"],
                        y=row["y"],
                        sizex = size,
                        sizey = size,
            #             sizex=np.sqrt(row["pop"] / df["pop"].max()) * maxi * 0.2 + maxi * 0.05,
            #             sizey=np.sqrt(row["pop"] / df["pop"].max()) * maxi * 0.2 + maxi * 0.05,
                        sizing="contain",
                        opacity=opacity,
                        # layer="above"
                    )
                )

            # fig.update_layout(height=600, width=1000,, plot_bgcolor="#dfdfdf")

        return fig