import sys
import time
sys.path.append('/home/virgaux/dataforgood/bechdelai/bechdelai')

from model import Classifier, Detector

classifier = Classifier("/inputs/nudeModel/model/classifier_model.onnx")
detector = Detector("/inputs/nudeModel/model/detector_v2_default_checkpoint.onnx", "/inputs/nudeModel/model/detector_v2_default_classes")

res_detector = detector.make_pred('/inputs/bechdelia/exemple_2.jpeg')
print(res_detector)