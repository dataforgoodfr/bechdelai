import os
import math
import cv2
import tensorflow as tf
from tensorflow.train import Features, Example, Feature
from tqdm import trange

class Extract_One_Video:

    def __init__(self, video_path:str, folder_outputs = "outputs", frame_rate = 5) -> None:
        self.frame_rate = frame_rate
        self.video_path = video_path
        self.outputs = folder_outputs

    def _read_video_classic(treatment_fun, video_path, frame_rate):
        count = 0
        cap = cv2.VideoCapture(video_path) # capturing the video from the given path
        frameRate = cap.get(frame_rate) # frame rate
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Define the number of frames

        for _ in trange(length, bar_format = "{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}"):

            frameId = cap.get(1) # current frame number
            ret, frame = cap.read()

            if (ret != True):
                raise "Problem de lecture de fichier !!"

            if frame_rate == 1 or (frameId % math.floor(frameRate) == 0):
                treatment_fun(frame, str(count))

            count +=1
                
        cap.release()

    def extract_info_from_videos(self, tf_records=True):
        """
        Cette fonction permet de lire la vidéo et construire un dossier avec les enregistrements.
        """

        if not tf_records:
            self._read_video_classic(self.create_jpeg, self.video_path, self.frame_rate)
                
        else:
            self._read_video_classic(self.create_tfrecord_simple, self.video_path, self.frame_rate)



    def create_jpeg(frame, output_name):
        filename = os.path.join(output_name + ".jpg")
        cv2.imwrite(filename, frame)



    def create_tfrecord_simple(frame, output_name):
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
        with tf.io.TFRecordWriter(output_name, option) as f:
            f.write(person_example.SerializeToString())