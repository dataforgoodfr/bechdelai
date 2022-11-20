
import pandas as pd
from transformers import ViltProcessor, ViltForQuestionAnswering
from PIL import Image

class ViLT:
    def __init__(self):
        
        # Load model from Hugging Face Modelhub
        print("Loading ViLT model")
        self.processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
        self.model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")


    def predict(self,images,text,th = 0.01):

        if isinstance(images,list):
            text = [text]*len(images)

        # prepare inputs
        inputs = self.processor(images = images, text = text, return_tensors="pt",padding=True)

        # forward pass
        outputs = self.model(**inputs)
        preds = outputs.logits
        probas = preds.softmax(dim=1)
        probas = pd.DataFrame(probas.detach().numpy()).rename(columns = self.model.config.id2label)

        # Format to ge only the best results
        preds = []
        for i,row in probas.iterrows():
            values = [(k,v) for k,v in row.sort_values(ascending = False).where(lambda x : x > th).dropna().to_dict().items()]
            preds.append(values)
        preds = pd.DataFrame(preds)

        return preds,probas
