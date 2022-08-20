import pandas as pd
import numpy as np
from transformers import CLIPProcessor, CLIPModel
from scipy.special import softmax


class CLIP:

    """
    Permet de déterminer une action à partir des images d'un film
    """

    def __init__(self,prompts = None):
        
        # Load CLIP model from Hugging Face Modelhub
        print("Loading CLIP model")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.prompts = prompts


    def predict_action(self, im):

        inputs = self.processor(text=self.prompts, images=im, return_tensors="pt", padding=True)
        # Predict probabilities using CLIP model
        outputs = self.model(**inputs)
        preds = outputs.logits_per_image # this is the image-text similarity score
        probas = preds.softmax(dim=1) # we can take the softmax to get the label probabilities
        idx = np.argmax(probas.detach())

        return {
            "Label":self.prompts[idx],
            "Proba":str(probas[0].detach().numpy()[idx]),
            "Proximity":str(preds[0].detach().numpy()[idx]),
        }
