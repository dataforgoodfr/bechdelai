import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from ipywidgets import widgets, interact
from transformers import CLIPProcessor, CLIPModel

from .video import Video


class CLIP:
    def __init__(self):
        
        # Load CLIP model from Hugging Face Modelhub
        print("Loading CLIP model")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def predict(self,images:list,prompts:list,probas = True) -> pd.DataFrame:

        # Convert Video object input as list of PIL Images
        # You can also use directly list of PIL images as input
        if isinstance(images,Video):
            images = [x.img for x in images.frames]

        # Process inputs using CLIP processor
        inputs = self.processor(text=prompts, images=images, return_tensors="pt", padding=True)

        # Predict probabilities using CLIP model
        outputs = self.model(**inputs)
        preds = outputs.logits_per_image # this is the image-text similarity score
        probas = preds.softmax(dim=1) # we can take the softmax to get the label probabilities

        # Convert to dataframe
        preds = pd.DataFrame(preds.detach().numpy(),columns = prompts)
        probas = pd.DataFrame(probas.detach().numpy(),columns = prompts)

        return preds,probas


    def show_preds_area(self,preds):
        fig = px.area(preds)
        return fig


    def show_preds_by_image(self,preds,i):
        preds.iloc[i].sort_values(ascending = False).plot(kind = "bar",figsize = (15,3))
        plt.xticks(rotation=45,horizontalalignment = "right")
        plt.title(f"Labels for frame {i}")
        plt.show()


    def replay(self,images:list,preds:pd.DataFrame,interval:float=0.5):

        # Convert Video object input as list of PIL Images
        # You can also use directly list of PIL images as input
        if isinstance(images,Video):
            images = [x.img for x in images.frames]

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

        display(slider)
