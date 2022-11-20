import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
 
from .frame import Frame

"""
TODO
Other option would be using RetinaFace python library or directly using DeepFace
"""


FACE_CASCADE_PATH = "haarcascade_frontalface_default.xml"

class FaceDetector:
    def __init__(self):
        """
        Explanation of OpenCV arguments https://stackoverflow.com/questions/36218385/parameters-of-detectmultiscale-in-opencv-using-python
        """
        self.cascade = cv2.CascadeClassifier(os.path.join(cv2.data.haarcascades,FACE_CASCADE_PATH))


    def predict(self,img,scale_factor = 1.3,min_neighbors = 5):
        # TODO add 1.3 and 5 as argument
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray, scale_factor, min_neighbors)
        return faces

    def extract(self,img,faces):

        rois = []

        for (x,y,w,h) in faces:
            roi = img[y:y+h, x:x+w]
            roi = Image(array = roi)
            rois.append(roi)

        return rois


    def show(self,img,faces = None,**kwargs):


        if faces is None:
            faces = self.predict(img,**kwargs)
        
        img_copy = np.copy(img)

        for (x,y,w,h) in faces:
            cv2.rectangle(img_copy,(x,y),(x+w,y+h),(255,0,0),2)

        plt.imshow(img_copy)
        plt.show()
