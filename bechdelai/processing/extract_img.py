import os
import math
import cv2
import json
import tensorflow as tf
from tensorflow.train import Features, Example, Feature
from tqdm import trange

class Extract_One_Video:

    def __init__(self, video_path:str, folder_outputs = "outputs", frame_rate = 5, details=True) -> None:
        self.frame_rate = frame_rate
        self.video_path = video_path
        self.outputs = os.path.join(folder_outputs, self.video_path.replace('.mp4', ''))
        self.details = details

    def _creat_archi(self):
        os.makedirs(self.outputs, exist_ok=True)

    def _read_video_classic(self, treatment_fun):
        self._creat_archi()
        count = 0
        cap = cv2.VideoCapture(self.video_path) # capturing the video from the given path
        frameRate = cap.get(self.frame_rate) # frame rate
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Define the number of frames

        for _ in trange(length, bar_format = "{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}"):

            frameId = cap.get(1) # current frame number
            ret, frame = cap.read()

            if (ret != True):
                raise "Problem de lecture de fichier !!"

            if self.frame_rate == 1 or (frameId % math.floor(frameRate) == 0):
                treatment_fun(frame, os.path.join(self.outputs,str(count)))

            count +=1
                
        cap.release()

    def extract_info_from_videos(self, tf_records=True, detail=None):
        """
        Cette fonction permet de lire la vidéo et construire un dossier avec les enregistrements.
        """

        if not tf_records:
            self._read_video_classic(self.create_jpeg)
                
        else:
            self._read_video_classic(self.create_tfrecord_video)
            if detail:
                self.create_tfrecord_detail(detail)



    def create_jpeg(self, frame, output_name):
        filename = os.path.join(output_name + ".jpg")
        cv2.imwrite(filename, frame)



    def create_tfrecord_video(self, frame, output_name):
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
    

    def _lecteur_json(self, filename):
        with open(filename) as json_data:
            data_dict = json.load(filename)

        return data_dict

    def create_tfrecord_detail(self, detail_json_path):

        dict_json = self._lecteur_json(detail_json_path)

        author = tf.train.BytesList(value=[dict_json["author"]])
        lenght = tf.train.Int64List(value=[dict_json["lenght"]])
        title = tf.train.BytesList(value=[dict_json["title"]])
        description = tf.train.BytesList(value=[dict_json["description"]])
        date = tf.train.BytesList(value=[dict_json["description"]])
        views = tf.train.Int64List(value=[dict_json["views"]])

        """
        "keywords": video.keywords,
        "image_desc": img.tolist()
        """

        person_example = Example(
            features = Features(
                feature = {
                    "author": Feature(bytes_list = author),
                    "lenght": Feature(int64_list = lenght),
                    "title": Feature(bytes_list = title),
                    "description": Feature(bytes_list = description),
                    "date": Feature(bytes_list = date),
                    "views": Feature(int64_list = views),
                }
            )
        )

        #Ecrit les fichier tfrecords
        option = tf.io.TFRecordOptions(compression_type="GZIP")
        with tf.io.TFRecordWriter(self.outputs + "/" + "detail.record", option) as f:
            f.write(person_example.SerializeToString())