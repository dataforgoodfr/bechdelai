import numpy as np
import matplotlib.pyplot as plt
from model.output_creator.face_result import Result_Face_Creator

class BechdelVision:

    def __init__(self, dataset, face_detector_model, face_classifier_model = None, mode = "minimal") -> None:
        self.dataset = dataset
        self.face_detector_model = face_detector_model
        self.face_classifier_model = face_classifier_model
        self.mode = mode
        self.writer = self._define_writer()

    def _define_writer(self):
        if self.mode == "minimal":
            return Result_Face_Creator()

    def predict_dataset(self):
        num_batch = 0

        for im_batch in self.dataset:
            list_pred = []

            for im in im_batch:
                
                if self.mode == "minimal":
                    pred_im = self.face_detector_model.deeprecognition(im)

                elif self.mode == "medium":
                    pred_im = self.face_detector_model.deeprecognition(im, image=True)
                    print(self.face_classifier_model.make_pred(pred_im))

                if len(pred_im)>0:
                    list_pred.append(pred_im)


            if len(list_pred)>0 and self.mode == "minimal":
                self.writer.write_minimal_batch_res(list_pred, num_batch)
            
            num_batch+=1


