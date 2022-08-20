from model.output_creator.data_result import Result_Face_Creator

class BechdelVision:

    def __init__(self,
            file_loader,
            face_detector_model,
            face_classifier_model = None,
            face_embedding_model = None,
            action_detector = None,
            mode = "minimal", 
            output = "output") -> None:

        self.file_loader = file_loader
        self.dataset = self.file_loader.load_dataset()

        self.face_detector_model = face_detector_model
        self.face_classifier_model = face_classifier_model
        self.face_embedding_model = face_embedding_model
        self.action_detector = action_detector

        self.mode = mode
        self.output = output
        self.writer_data = Result_Face_Creator(output_dir = self.output)


    def _predict_minimal(self, im, image = False):
        pred_im = self.face_detector_model.deeprecognition(im, image=image)
        if len(pred_im)>0:
            return pred_im

    def _predict_medium(self, im):
        # L'analyse medium permettra de connaître Genre, Age, Sentiment de perso uniques
        # On a donc besoin de détection, embedding, classifier

        pred_f = self._predict_minimal(im, image=True)
        if pred_f:
            embedding = self.face_embedding_model.make_embeddings(pred_f[0])
            pred_spec = self.face_classifier_model.make_pred(pred_f[0])
            return [pred_f[1], pred_spec, embedding]

    def _predict_large(self, im):
        med_pred = self._predict_medium(im)
        if med_pred:
            if len(med_pred[0])>1:
                action_pred = self.action_detector.predict_action(im.numpy())
                med_pred.append(action_pred)
                return med_pred
            else:
                med_pred.append(None)
                return med_pred

        return med_pred

    def predict_dataset(self):

        num_batch = 0
        for im_batch in self.dataset:
            list_pred = []
            for im in im_batch:
                if self.mode == "minimal":
                    pred = self._predict_minimal(im)
                    if pred:
                        list_pred.append(pred)
                elif self.mode == "medium":
                    pred = self._predict_medium(im)
                    if pred:
                        list_pred.append(pred)

                elif self.mode == "large":
                    pred = self._predict_large(im)
                    if pred:
                        list_pred.append(pred)
            
            if len(list_pred)>0 and self.mode == "minimal":
                self.writer_data.write_minimal_batch_res(list_pred, num_batch)
            elif len(list_pred)>0 and self.mode == "medium":
                self.writer_data.write_medium_batch_res(list_pred, num_batch)
            elif len(list_pred)>0 and self.mode == "large":
                self.writer_data.write_large_batch_res(list_pred, num_batch)
            num_batch+=1


