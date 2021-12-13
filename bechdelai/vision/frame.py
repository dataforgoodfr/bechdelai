
import numpy as np
from PIL import Image
from IPython.display import Image as JupyterImage
from deepface import DeepFace

class Frame:
    def __init__(self,path = None,array = None):

        if path is not None:
            self.img = Image.open(path)
        elif array is not None:
            self.img = Image.fromarray(array)
        else:
            raise Exception("You have to provide one input")

    def _repr_png_(self):
        return self.img._repr_png_()

    def resize(self,size = None,width = None,height = None):

        w,h = self.img.size

        if size is not None:
            self.img = self.img.resize(size)
        elif width is not None:
            if width < 1:
                width = int(width * w)
                self.resize(width = width)
            else:
                height = int((width/w) * h)
                self.img = self.img.resize((width,height))

        elif height is not None:
            if height < 1:
                height = int(height * h)
                self.resize(height = height)
            else:
                width = int((height/h) * w)
                self.img = self.img.resize((width,height))

    def save(self):
        pass


    @property
    def array(self):
        return np.array(self.img)

    def show(self):
        return self.img

    def extract_faces(self,detector,scale_factor = 1.1,min_neighbors = 3):
        img = self.array
        self.faces = detector.predict(img,scale_factor,min_neighbors) 
        self.faces = detector.extract(img,self.faces)
        return self.faces

    def detect_faces(self,detector,):
        pass

    def show_faces(self,detector,scale_factor = 1.1,min_neighbors = 3):
        detector.show(self.array,scale_factor = scale_factor,min_neighbors = min_neighbors)


    def analyze(self,**kwargs):
        """Analyse frame using DeepFace pretrained models
        Works only if frame is already a face
        """
        return DeepFace.analyze(self.array,prog_bar = False,**kwargs)