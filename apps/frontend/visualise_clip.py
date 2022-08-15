import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from ipywidgets import widgets, interact
import pandas as pd

def replay(self,images:list,preds:pd.DataFrame,interval:float=0.5):

    # Convert Video object input as list of PIL Images
    # You can also use directly list of PIL images as input
    # if isinstance(images,Video):
    try:
        images = [x.img for x in images.frames]
    except:
        pass

    # Prepare widgets
    play = widgets.Play(
        value=0,
        min=0,
        max=len(images) - 1,
        step=1,
        interval=interval * 1000,
        description="Press play",
        disabled=False,
    )

    slider = widgets.IntSlider(min=0, value=0, max=len(images) - 1, step=1)
    widgets.jslink((play, "value"), (slider, "value"))

    # Visualize frames and widgets
    @interact(i=play)
    def show(i):
        self.show_preds_by_image(preds,i)
        return images[i]

def show_preds_area(self,preds):
    fig = px.area(preds,color_discrete_sequence=px.colors.qualitative.Alphabet)
    return fig


def show_preds_by_image(self,preds,i):
    preds.iloc[i].sort_values(ascending = False).plot(kind = "bar",figsize = (15,3))
    plt.xticks(rotation=45,horizontalalignment = "right")
    plt.title(f"Labels for frame {i}")
    plt.show()
