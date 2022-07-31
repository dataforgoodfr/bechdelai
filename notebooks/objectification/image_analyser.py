"""
Ce fichier permet l'analyse d'une scène, le but est de l'appliquer à chaque frame pour analyser à terme les infos extraites
"""

# Import module
from nudenet import NudeClassifier
from nudenet import NudeDetector
import json

BATCH_SIZE = 4

# initialize detector (downloads the checkpoint file automatically the first time)
classifier = NudeClassifier(model_path = "/inputs/nudeModel/model/classifier_model.onnx") # detector = NudeDetector('base') for the "base" version of detector.
detector = NudeDetector(checkpoint_path="/inputs/nudeModel/model/detector_v2_default_checkpoint.onnx", classes_path="/inputs/nudeModel/model/detector_v2_default_classes")


res_classifier = classifier.classify(['/inputs/bechdelia/exemple.jpeg', '/inputs/bechdelia/exemple_2.jpeg'],  batch_size=2)
res_detector = detector.detect('/inputs/bechdelia/exemple_2.jpeg')

print(res_classifier)
print(res_detector)

LINK_OUTPUT = "/outputs/resultnude/resdetector.json"

# Serializing json
json_object = json.dumps(res_detector, indent=4)
 
# Writing to sample.json
with open(LINK_OUTPUT, "w") as outfile:
    outfile.write(json_object)