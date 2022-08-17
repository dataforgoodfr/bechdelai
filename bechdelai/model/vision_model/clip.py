import pandas as pd
import numpy as np
from transformers import CLIPProcessor, CLIPModel
from scipy.special import softmax
from ..output_creator.perso_action_result import Result_Action_Creator


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


    def predict_batch(self, btch_im:list):

        inputs = self.processor(text=self.prompts, images=btch_im, return_tensors="pt", padding=True)
        # Predict probabilities using CLIP model
        outputs = self.model(**inputs)
        preds = outputs.logits_per_image # this is the image-text similarity score
        probas = preds.softmax(dim=1) # we can take the softmax to get the label probabilities

        return preds, probas

    def predict(self, dataset, probas = True, size = None) -> pd.DataFrame:

        res_crea = Result_Action_Creator()
        if size:
            data = iter(dataset)
            for i in range(size):
                inference = self.predict_batch([i for i in next(data).numpy()])
                res_crea.write_batch_res(inference, self.prompts, i)
        else:
            cpt = 0
            for batch_im in dataset:
                inference = self.predict_batch([i for i in batch_im.numpy()])
                res_crea.write_batch_res(inference, self.prompts, cpt)
                cpt+=1


        # Convert to dataframe
        #preds = pd.DataFrame(preds.detach().numpy(),columns = prompts)
        #probas = pd.DataFrame(probas.detach().numpy(),columns = prompts)

        #return preds,probas