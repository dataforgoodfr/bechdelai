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


    def predict_batch(self, btch_im:list):

        inputs = self.processor(text=self.prompts, images=btch_im, return_tensors="pt", padding=True)
        # Predict probabilities using CLIP model
        outputs = self.model(**inputs)
        preds = outputs.logits_per_image # this is the image-text similarity score
        probas = preds.softmax(dim=1) # we can take the softmax to get the label probabilities

        return preds, probas

    def predict(self, dataset, probas = True, size = None) -> pd.DataFrame:

        if size:
            data = iter(dataset)
            for _ in range(size):
                inference = self.predict_batch([i for i in next(data).numpy()])
        else:
            for batch_im in dataset:
                inference = self.predict_batch([i for i in batch_im.numpy()])
                print(inference)


        # Convert to dataframe
        #preds = pd.DataFrame(preds.detach().numpy(),columns = prompts)
        #probas = pd.DataFrame(probas.detach().numpy(),columns = prompts)

        #return preds,probas



    def reduce_preds_by_category(self,preds):   
        reduced_preds = []
        for category, cols in self.prompts_dict.items():
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