import os
import math
import cv2
import tensorflow as tf
from tensorflow.train import Features, Example, Feature
from tqdm import trange

class Extract_Video_YT:

    def __init__(self, youtube_link:str, output_dir=".") -> None:
        self.yl = youtube_link
        self.output_dir = output_dir

    def _create_archi(self):
        os.mkdir(self.output_dir, exist_ok = True)

    def download_video(self):
        os.system("youtube-dl -g -f mp4 " + self.yl)


class Extract_Features:

    def __init__(self, video_dir:str, frame_rate = 5) -> None:
        self.frame_rate = frame_rate
        self.video_dir = video_dir

    def extract_frames_from_videos(self, tf_records=True):
        """
        Cette fonction permet de lire la vidéo et construire un dossier avec les enregistrements.
        """

        count = 0
        cap = cv2.VideoCapture(path) # capturing the video from the given path
        frameRate = cap.get(self.frame_rate) # frame rate
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Define the number of frames

        for _ in trange(length, bar_format = "{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}"):

            frameId = cap.get(1) # current frame number
            ret, frame = cap.read()
            if (ret != True):
                break

            if self.frame_rate == 1 or (frameId % math.floor(frameRate) == 0):
                if not tf_records:
                    filename = os.path.join(folder,f"frame{count}.jpg")
                    cv2.imwrite(filename, frame)
                    
                else:
                    create_tfrecord(frame, folder + "/" + str(frameId) + ".tfrecord")

                count +=1
                
        cap.release()

    def create_tfrecord(frame, name):
        """
        Pour le moment on a juste l'image en entrée mais on pourrait ajouter plusieurs information dans le même fichier
        """

        byte_list = tf.train.BytesList(value=[tf.io.encode_jpeg(frame).numpy()])
        person_example = Example(
            features = Features(
                feature = {
                    "image": Feature(bytes_list = byte_list),
                }
            )
        )

        #Ecrit les fichier tfrecords
        option = tf.io.TFRecordOptions(compression_type="GZIP")
        with tf.io.TFRecordWriter(name, option) as f:
            f.write(person_example.SerializeToString())