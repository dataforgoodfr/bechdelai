import cv2
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from PIL import Image

def show_faces_on_image(img,rois,width = 2,color = (255,0,0),genders = None):

    new_img = np.copy(img)

    if not isinstance(color,list):
        color = [color]*len(rois)

    if genders is not None:
        color = [(255,0,0) if x == "man" else ((172, 239, 159) if x == "woman" else (30, 31, 28)) for x in genders]

    if rois is not None:
        for i,values in enumerate(list(rois.values())):
            (x1,y1,x2,y2) = values["facial_area"]
            cv2.rectangle(new_img,(x1,y1),(x2,y2),color[i],width)

    new_img = Image.fromarray(new_img)
    return new_img



def show_all_faces(faces,columns = 10,figsize_row = (15,1),titles = None):

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
