from data.stream import Extract_Video_Stream
from bechdelai.model.vision_model.face_detector import OpenCV_Detector, DeepRetina_Detector


detector = OpenCV_Detector()
Extract_Video_Stream("https://www.tf1.fr/tf1/direct", quality="worst").read_video(detector.deep_recognition)