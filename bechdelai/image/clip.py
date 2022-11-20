import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from ipywidgets import widgets, interact
from transformers import CLIPProcessor, CLIPModel
from scipy.special import softmax


class CLIP:
    def __init__(self,prompts_dict = None):
        
        # Load CLIP model from Hugging Face Modelhub
        print("Loading CLIP model")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        if prompts_dict is not None:
            self.set_prompts(prompts_dict)

    def set_prompts(self,prompts_dict):
        self.prompts_dict = prompts_dict

    @property
    def prompts(self):
        return pd.DataFrame([(k,x) for k,v in self.prompts_dict.items() for x in v],columns = ["category","prompt"])

    @property
    def prompts_list(self):
        return self.prompts["prompt"].tolist()

    def predict(self,images:list) -> pd.DataFrame:

        # Convert Video object input as list of PIL Images
        # You can also use directly list of PIL images as input
        # if isinstance(images,Video):
        try:
            images = [x.img for x in images.frames]
        except:
            pass

        # Get prompts
        prompts = self.prompts_list

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
        fig = px.area(preds,color_discrete_sequence=px.colors.qualitative.Alphabet)
        return fig


    def show_preds_by_image(self,preds,i):
        preds.iloc[i].sort_values(ascending = False).plot(kind = "bar",figsize = (15,3))
        plt.xticks(rotation=45,horizontalalignment = "right")
        plt.title(f"Labels for frame {i}")
        plt.show()


    def reduce_preds_by_category(self,preds):   
        reduced_preds = []
        for category,cols in self.prompts_dict.items():
            if len(cols) > 0:
                preds_category = self.reduce_preds_on_max(preds[cols])
                # preds_category = softmax(preds_category,axis = 1)
                reduced_preds.append(preds_category)
        reduced_preds = pd.concat(reduced_preds,axis = 1)
        reduced_preds = softmax(reduced_preds,axis = 1).round(4)
        return reduced_preds


    def reduce_preds_on_max(self,preds):
        preds_reduced = preds * (preds == np.repeat(preds.max(axis = 1).values[:,np.newaxis],len(preds.columns),axis = 1))
        return preds_reduced        

    def make_category_preds(self,preds,category,control = "base"):
        
        # Copy prediction for the category
        preds_category = preds[self.prompts_dict[category]].copy()

        # Control if the category is the best description of the frames
        control = preds[self.prompts_dict[category]].max(axis = 1) < preds[self.prompts_dict[control]].max(axis = 1)
        
        # Compute softmax and set to 0 if not majoritary
        preds_category = softmax(preds_category,axis = 1)
        preds_category.loc[control] = 0
        return preds_category


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

        display(slider)
