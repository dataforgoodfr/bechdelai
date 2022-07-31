# Import module
from nudenet import NudeClassifier
from nudenet import NudeDetector
import json

LINK_OUTPUT = "/outputs/resultnude/resdetector.json"

class Classifier:
    """
    Classify nude images
    """
    def __init__(self, model_path) -> None:
        #Care if you don't have the model in your 
        self.classifier = NudeClassifier(model_path)

    def make_pred(self, images, batch, output_path = None):
        
        pred = self.classifier.classify(images, batch_size=batch)
        if output_path:
            try:
                with open(LINK_OUTPUT, "w") as outfile:
                    outfile.write(pred)
                return 0
            except:
                raise "Error file creation"

        return pred

class Detector:
    """
    Detect image part that are sensibles
    """
    def __init__(self, model_path, class_path) -> None:
        #Care if you don't have the model in your 
        self.detector = NudeDetector(model_path, class_path)

    def make_pred(self, image, output_path = None):

        pred = self.detector.detect(image)
        if output_path:
            try:
                with open(LINK_OUTPUT, "w") as outfile:
                    outfile.write(pred)
                return 0
            except:
                raise "Error file creation"
        return pred
