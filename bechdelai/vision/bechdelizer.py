import os
import pandas as pd
import numpy as np
import cv2
import math
import sys
sys.path.append("../../")
from bechdelai.vision.frame import Frame
from bechdelai.vision.face_detection import FaceDetector
from bechdelai.vision.clip import CLIP
from bechdelai.vision.video import Video


class Bechdelizer:
    
    def __init__(self):
        self.video_path = '../../data/sample_videos/Andy Samberg dances on Megatron Man.mp4'
        self.result_dir = 'tempDir'
        self.frame_path = self.result_dir + '/frames'
    
    def create_output_directory(self,folder):
        if not os.path.exists(folder):
            mode = 0o666
            os.mkdir(folder, mode)
            print('folder {} created'.format(folder))

        files_list = os.listdir(folder)
        print('{} are going to be deleted'.format(len(files_list)))
        if len(files_list) > 0:
            for file_name in files_list:
                file_path = os.path.join(folder, file_name)
                if os.path.isfile(file_path):
                    print('Deleting file:', file_path)
                    os.remove(file_path)
        return None

    def predict_gender_deepface(self,frame_path):
        """From a directory containing frames, this function will analyse the gender of each character in each frame
        Parameters
        ---------
        frame_path: Str
            Path to the directory with Frames (image in jpg)
        Return
        ------------
        list_gender : List
            List containing the gender predicted for each frames
        frames : 
            List of object containing frames and attribute such as faces
        """
        detector = FaceDetector()
        frames = Frame(frame_path)
        frames.resize(width = 600)
        faces = frames.extract_faces(
            detector = detector,
            #deepface_check = True,
            scale_factor = 1.3,
            min_neighbors = 3,
            #face_size = (200,200),
            #deepface_backend = "ssd"
        )
        return faces
        #list_gender = []
        #faceid = 0
        #if faces is not None:
        #    print('len faces : {}'.format(len(faces)))
        #    for face in faces:
        #        print(type(face))
        #        faceid =+ 1
        #        prediction = face.analyze(actions = ['gender'])
        #        gender_pred = prediction['gender']
        #        list_gender.append(gender_pred)
        #        filename = os.path.join('frames_w_faces', f"face{faceid}.jpg")
        #        cv2.imwrite(filename, face)
        #else:
        #    list_gender.append(None)
        #return list_gender


    def women_detection_deepface(self, video_path,image_dir=None, time_rate=1):
        """From a video and given frame raate, this function will check the presence of women on
            some specific frames with DeepFace Model
        Parameters
        ---------
        video_path: Str
            Path to the video
        time_rate: Int
            Number of second between each frames that are processed (eg : if 2, one frame will be processed every 2 sec)
        image_dir : Str
            Path to the output directory to store all processed frames 
        Return
        ------------
        df : Pandas DataFrame
            DataFrame with all frames and the detections if 2 women were found
        face_list : List
            List of images of all faces 
        """
        if image_dir is None:
            image_dir = 'tempDir/frames'
            
        self.create_output_directory(image_dir)

        file_list = []
        pred_list = []
        list_nb_woman = []
        timestamps = []
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(fps)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        framerate = fps * time_rate
        frame_processed = round(frame_count/framerate)
        print('{} frames are about to be processed and registred in a csv'.format(frame_processed))

        count_frame_woman = 0
        while(cap.isOpened()):
            frameId = cap.get(1)
            frame_exists, curr_frame = cap.read()
            if (frame_exists != True):
                break

            if (frameId % math.floor(framerate) == 0):
                timestamp = round(cap.get(cv2.CAP_PROP_POS_MSEC)/1000)
                timestamps.append(timestamp)
                filename = os.path.join(image_dir, f"frame{frameId}.jpg")
                cv2.imwrite(filename, curr_frame)
                file_list.append(filename)
                gender_list = self.predict_gender_deepface(filename)
                pred_list.append(gender_list)
                
                nb_woman =  gender_list.count('Woman')
                list_nb_woman.append(nb_woman)

                if nb_woman > 1:
                    count_frame_woman =+ 1
        
        df = pd.DataFrame({'timestamp' : timestamps,
                            'file_location': file_list,
                            'prediction': pred_list,
                            'nb_woman_detected':list_nb_woman})
 
        print('At least 2 womens speaking together have been detected {} times'.format(count_frame_woman))

        return df


if __name__ == '__main__':

    Bechdelizer = Bechdelizer()
    #Analysing if women are in a frame with DeepFace
    df = Bechdelizer.women_detection_deepface(video_path = Bechdelizer.video_path,
                                                        time_rate=2)
    #Analysing if women are in a frame with CLIP
    clip = CLIP()
    video = Video(Bechdelizer.frame_path)
    #Defining label for Clip
    prompts=  ['two women speaking',
                'group of ladies speaking',
                'several girls discussing']
            
    video.resize(width = 600)
    preds,probas = clip.predict(video,prompts)
    frames = [df, probas]
    result = pd.concat(frames, axis=1)
    result.to_csv(Bechdelizer.result_dir+'/table_result/'+'prediction_enriched_clip.csv')

    #Reste a déterminer le seuil de probas pour CLIP qui permet d'être suffisamment sûr
    # pour affichier que plusieurs femmes sont présentes à l'images