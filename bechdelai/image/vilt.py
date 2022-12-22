
import pandas as pd
import numpy as np
from tqdm.auto import tqdm
from transformers import ViltProcessor, ViltForQuestionAnswering
from PIL import Image

class ViLT:
    def __init__(self):
        
        # Load model from Hugging Face Modelhub
        print("Loading ViLT model")
        self.processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
        self.model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")


    def predict_many(self,images,questions):

        if not isinstance(questions,list): questions = [questions]

        preds = []
        probas = []

        for i,image in enumerate(tqdm(images)):

            preds_i,probas_i = self.predict(image,questions)

            for j,question in enumerate(questions):
                preds_i[j].insert(0,"question",question)
                preds_i[j].insert(0,"image_id",i)

            preds.extend(preds_i)
            probas.append(probas_i)

        preds = pd.concat(preds,axis = 0,ignore_index = True)

        return preds,probas

        # all_preds = []

        # for k in texts:

        #     preds[k] = pd.DataFrame(preds[k],columns = ["pred","proba"]) 
        #     probas[k] = pd.DataFrame(probas[k],index = range(len(images)))

        #     preds_k = preds[k].copy().drop(columns = ["proba"]).rename(columns = {"pred":k})
        #     all_preds.append(preds_k)

        # all_preds = pd.concat(all_preds,axis = 1)

        

        return preds,probas,all_preds


    def predict(self,image,questions,n = 5):

        if isinstance(image, np.ndarray):
            image_to_predict = image
        else:
            image_to_predict = image.array

        # if isinstance(images,list):
        #     text = [text]*len(images)
        # Possible to pass several images but you need more RAM than on a single computer
        # Preferable in this version to simply use a for loop
        # is it possible to pass several queries ?

        # prepare and normalize inputs
        if not isinstance(questions,list): questions = [questions]
        image_to_predict = [image_to_predict] * len(questions)
        assert len(image_to_predict) == len(questions)

        # prepare inputs
        inputs = self.processor(images = image_to_predict, text = questions, return_tensors="pt",padding=True)

        # forward pass
        outputs = self.model(**inputs)
        preds = outputs.logits
        probas = preds.softmax(dim=1)
        probas = pd.DataFrame(probas.detach().numpy()).rename(columns = self.model.config.id2label)
        probas.index = questions

        # Format to get the best preds
        preds_list = []
        probas_list = []
        for question,row in probas.iterrows():

            preds = row.sort_values(ascending = False).head(n).reset_index().reset_index()
            preds.columns = ["rank","answer","proba"]
            preds_list.append(preds)
            probas_list.append(row)


        return preds_list,probas_list


        # # Format to ge only the best results
        # preds = []
        # for i,row in probas.iterrows():
        #     values = [(k,v) for k,v in row.sort_values(ascending = False).where(lambda x : x > th).dropna().to_dict().items()]
        #     preds.append(values)
        # preds = pd.DataFrame(preds)

        # return preds,probas
