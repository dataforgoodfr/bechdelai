from ..output_creator.face_result import Result_Face_Creator
import numpy as np

class BechdelVision:

    def __init__(self, dataset, result_writer, face_detector_model, face_classifier_model = None, mode = "complete") -> None:
        self.dataset = dataset
        self.result_writer = result_writer
        self.face_detector_model = face_detector_model
        self.face_classifier_model = face_classifier_model
        self.mode = "minimal"


    def predict_dataset(self, dataset, mode="minimal"):
        
        num_batch = 0

        for im_batch in dataset:
            list_pred = []

            for im in im_batch:
                im_np = np.float32(im.numpy())

                if mode == "minimal":
                    pred_im = self.deeprecognition(im_np)
                elif mode == "medium":
                    pred_im = self.deeprecognition(im_np)

                if len(pred_im)>0:
                    list_pred.append(pred_im)


            if len(list_pred)>0 and mode == "minimal":
                self.result_writer.write_minimal_batch_res(list_pred, num_batch)


            num_batch+=1


