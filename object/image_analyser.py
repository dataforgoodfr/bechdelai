"""
Ce fichier permet l'analyse d'une scène, le but est de l'appliquer à chaque frame pour analyser à terme les infos extraites
"""

# Import module
from nudenet import NudeClassifier
from nudenet import NudeDetector

BATCH_SIZE = 1

# initialize detector (downloads the checkpoint file automatically the first time)
classifier = NudeClassifier(model = "/inputs/nudeModel/classifier_model.onnx") # detector = NudeDetector('base') for the "base" version of detector.
detector = NudeDetector(checkpoint_path="/inputs/nudeModel/detector_v2_default_checkpoint.onnx", classes_path="/inputs/nudeModel/detector_v2_default_classes")

#print(classifier.classify('examples/sexy/sexy.jpeg'))
#print(detector.detect('examples/normal/normal.jpg'))

"""
detector.censor(
    'examples/normal/normal.jpg', 
    out_path='examples/normal/censored_normal.jpg', 
    visualize=True
)
"""