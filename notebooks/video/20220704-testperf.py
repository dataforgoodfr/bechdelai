import sys
sys.path.append('/home/virgaux/dataforgood/bechdelai/bechdelai')
import processing.extract_img
import processing.load_data
import data.youtube
import model.vision_model.clip
from bechdel_vision import BechdelVision
from model.vision_model.face_detector import OpenCV_Detector, DeepRetina_Detector
from model.vision_model.face_classifier import DeepFaceBech
from model.output_creator.face_result import Result_Face_Creator


#DOWNLOAD DATA
#downloader = data.youtube.Extract_Video_YT("https://www.youtube.com/watch?v=W0vCddpZ3WI&list=RDGMEMECQexVIf8HjAQgdybEHXKwVMW0vCddpZ3WI&start_radio=1")
#downloader.download_video()


#EXTRACT DATA
#extractor = processing.extract_img.Extract_One_Video("/home/virgaux/dataforgood/bechdelai/data/sample_video_yt/Benjamin Biolay - Miss Miss.mp4")
#extractor.extract_info_from_videos()


#LOAD DATASET
loader = processing.load_data.LoaderData("/home/virgaux/dataforgood/bechdelai/data/sample_video_yt/Benjamin Biolay - Miss Miss")
dataset = loader.load_dataset()


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
bechvision = BechdelVision(dataset, OpenCV_Detector(), DeepFaceBech(caracteristique=['age', 'gender', 'race', 'emotion']), mode = "medium")
bechvision.predict_dataset()

#DISPLAY DATA
#displayer = processing.load_data.Displayer(dataset)
#displayer.show_img()