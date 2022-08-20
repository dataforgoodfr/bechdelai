import cv2
from retinaface import RetinaFace
import os
import numpy as np


class DeepRetina_Detector:

    """
    Il s'agit d'une technique efficace mais semble un peu lente à voir quand on testera sur GPU
    """

    def __init__(self) -> None:
        pass

    def _preprocess(self, frame):
        return frame.numpy().astype("uint8")

    def deeprecognition(self, frame:np.array,  image=False, rectangle = False):
        """
        Permet de faire des prédictions etdans les différents cas :

        image: Récupère juste les visages détectés
        rectangle: Récupère les images complètes avec un rectangle sur le visage détecté
        """

        frame = self._preprocess(frame)
        faces = RetinaFace.detect_faces(frame)
        
        if type(faces) is dict:
            only_face, lst_face = [], []
            for face in faces:
                identity = faces[face]
                facial_area = identity["facial_area"]
                if rectangle:
                    frame = cv2.rectangle(frame, (facial_area[2], facial_area[3]), (facial_area[0], facial_area[1]), (255, 0, 0), 1)
                elif image:
                    face = frame[facial_area[1]:facial_area[3], facial_area[0]:facial_area[2]]
                    only_face.append(face)
                    lst_face.append(identity["facial_area"])
                else:
                    lst_face.append(identity["facial_area"])
            if rectangle:
                return frame
            elif image:
                return only_face, lst_face
            return lst_face
        else:
            return []

class OpenCV_Detector:

    """
    Cette méthode est très efficace mais les deux paramètres à fixer sont plus difficile
    """

    def __init__(self, face_cascade_path="haarcascade_frontalface_default.xml", scale_factor = 1.2, min_neighbors = 4) -> None:
        
        #Explanation of OpenCV arguments https://stackoverflow.com/questions/36218385/parameters-of-detectmultiscale-in-opencv-using-python
        self.face_cascade_path = face_cascade_path
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors

    def _preprocess(self, frame):
        return frame.numpy().astype("uint8")
    
    def deeprecognition(self, frame, image=False, rectangle = False):

        frame = self._preprocess(frame)
        cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades, self.face_cascade_path))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, self.scale_factor, self.min_neighbors)

        if len(faces)>0 and rectangle:

            for (x,y,w,h) in faces:
                frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),1)
            return frame

        if len(faces)>0 and image:
            only_face = []
            for (x,y,w,h) in faces:
                only_face.append(frame[y:y+h, x:x+w])
            return only_face, faces


        elif len(faces)>0:
            return faces
        
        else:
            return []