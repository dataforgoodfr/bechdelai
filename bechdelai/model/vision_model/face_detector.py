import cv2
from retinaface import RetinaFace
import os
import numpy as np

#TODO : Il faut absolument faire une API à interoger pour avoir les prédictions GPU parce que du cloud on peut pas avoir les prédictions
# Dans le cas où y a pas d'API on pourra le faire en local

class DeepRetina_Detector:

    """
    Il s'agit d'une technique efficace mais semble un peu lente à voir quand on testera sur GPU
    """

    def __init__(self) -> None:
        pass

    def deep_recognition(self, frame:np.array):

        faces = RetinaFace.detect_faces(frame)

        if type(faces) is dict:
            for face in faces:
                identity = faces[face]
                facial_area = identity["facial_area"]
                frame = cv2.rectangle(frame, (facial_area[2], facial_area[3]), (facial_area[0], facial_area[1]), (255, 0, 0), 1)
            return frame
        else:
            return frame

class OpenCV_Detector:

    """
    Cette méthode est très efficace mais les deux paramètres à fixer sont plus difficile
    """

    def __init__(self, face_cascade_path="haarcascade_frontalface_default.xml", scale_factor = 1.2, min_neighbors = 4) -> None:
        
        #Explanation of OpenCV arguments https://stackoverflow.com/questions/36218385/parameters-of-detectmultiscale-in-opencv-using-python
        self.face_cascade_path = face_cascade_path
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors

    def deep_recognition(self, frame:np.array):

        # TODO add 1.3 and 5 as argument
        cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, self.face_cascade_path))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, self.scale_factor, self.min_neighbors)

        if len(faces)>0:
            for (x,y,w,h) in faces:
                frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),1)

        return frame