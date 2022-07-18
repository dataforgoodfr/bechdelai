from ctypes import resize


import numpy as np

class Preprocessor:

    def __init__(self,frame:np.array, resize = (None, None)) -> None:
        self.resize = resize
        self.frame = frame

    def _gpu_presence(self):
        print("courage pour installer cuda et opencv")