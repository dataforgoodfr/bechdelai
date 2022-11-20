
import numpy as np
from PIL import Image
from IPython.display import Image as JupyterImage
from deepface import DeepFace

class Img:
    def __init__(self,img):

        if isinstance(img,str):
            self.img = Image.open(img)
        elif isinstance(img,np.ndarray):
            self.img = Image.fromarray(img)
        elif isinstance(img,Image.Image):
            self.img = img
        else:
            raise Exception("You have to provide one input")

    def _repr_png_(self):
        return self.img._repr_png_()

    def resize(self,size = None,width = None,height = None,inplace = False):

        w,h = self.img.size

        new_img = self.img.copy()

        if size is not None:
            new_img = new_img.resize(size)
        elif width is not None:
            if width < 1:
                width = int(width * w)
            
            height = int((width/w) * h)
            new_img = new_img.resize((width,height))

        elif height is not None:
            if height < 1:
                height = int(height * h)

            width = int((height/h) * w)
            new_img = new_img.resize((width,height))

        

        if inplace:
            self.img = new_img
        else:
            return Img(new_img)

    def save(self):
        pass


    @property
    def array(self):
        return np.array(self.img)

    def show(self,resize = None):

        if resize is not None:
            new_img = Img(img.img.copy())
            return new_img.resize
        else:
            return self.img