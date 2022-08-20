import sys
sys.path.append('/home/virgaux/dataforgood/bechdelai/bechdelai')

import data.youtube
from model.vision_model.clip import CLIP
from utils.load_data import LoaderData
from bechdel_vision import BechdelVision
from model.vision_model.face_detector import OpenCV_Detector, DeepRetina_Detector
from model.vision_model.face_classifier import DeepFaceBech
from model.vision_model.face_embedding import FaceEmbedding


#DOWNLOAD DATA
#downloader = data.youtube.Extract_Video_YT("https://www.youtube.com/watch?v=W0vCddpZ3WI&list=RDGMEMECQexVIf8HjAQgdybEHXKwVMW0vCddpZ3WI&start_radio=1")
#downloader.download_video()


#EXTRACT DATA
#extractor = processing.extract_img.Extract_One_Video("/home/virgaux/dataforgood/bechdelai/data/sample_video_yt/Benjamin Biolay - Miss Miss.mp4")
#extractor.extract_info_from_videos()

"""
#MODEL ACTION
prompts= [
            'two women speaking',
            'group of ladies speaking',
            'several girls discussing',
        ]

clip_model = model.vision_model.clip.CLIP(prompts)
clip_model.predict(dataset)
"""

#FACE DETECTOR
bechvision = BechdelVision(LoaderData("/home/virgaux/dataforgood/bechdelai/data/sample_video_yt/Benjamin Biolay - Miss Miss"), 
                            OpenCV_Detector(), 
                            DeepFaceBech(caracteristique=['age', 'gender', 'race', 'emotion']),
                            FaceEmbedding(),
                            CLIP(['two women speaking','group of ladies speaking','several girls discussing',]),
                            mode = "large")
bechvision.predict_dataset()

#DISPLAY DATA
#displayer = processing.load_data.Displayer(dataset)
#displayer.show_img()