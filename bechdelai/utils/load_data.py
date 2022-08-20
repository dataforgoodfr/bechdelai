import tensorflow as tf
import cv2
import os
import matplotlib.pyplot as plt
from functools import partial

BATCH_SIZE = 5
AUTOTUNE = tf.data.AUTOTUNE
BUFFER_SIZE = 2048

IMAGE_DESC = {
    'image': tf.io.FixedLenFeature([], tf.string),
    }

DETAIL_DESC = {
    "author": tf.io.FixedLenFeature([], tf.string),
    "lenght": tf.io.FixedLenFeature([], tf.int64),
    "title": tf.io.FixedLenFeature([], tf.string),
    "description": tf.io.FixedLenFeature([], tf.string),
    "date": tf.io.FixedLenFeature([], tf.string),
    "views": tf.io.FixedLenFeature([], tf.int64),
}

class LoaderData:
    """
    Load Data in Tensorflow Dataset
    """

    def __init__(self, dir:str) -> None:
        self.dir = dir

    def _cvt(self, image):
        return cv2.cvtColor(image.numpy(), cv2.COLOR_BGR2RGB)

    def _tf_cv2_func(self, image):
        image = tf.py_function(self._cvt, [image], [tf.int32])
        return image[0]

    def lecture_img(self, example):
        """
        Permet de lire une image et la décoder pour passer de bytes à jpeg
        """

        example = tf.io.parse_single_example(example, IMAGE_DESC)
        img = tf.cast(example["image"], tf.string)

        img_decoded = tf.io.decode_jpeg(img, channels=3)
        img_cvt = self._tf_cv2_func(img_decoded)

        return img_cvt
    
    def lecture_detail(self, example):
        example = tf.io.parse_single_example(example, IMAGE_DESC)
        
        author = tf.cast(example["author"], tf.string)
        lenght = tf.cast(example["lenght"], tf.int64)
        title = tf.cast(example["title"], tf.string)
        description = tf.cast(example["description"], tf.string)
        date = tf.cast(example["date"], tf.string)
        views = tf.cast(example["views"], tf.int64)

        return {
            "Author": author,
            "Lenght": lenght,
            "Title": title,
            "Description": description,
            "Date": date,
            "Views": views
        }

    def load_dataset(self):
        """
        Charger les données
        """

        filenames = [self.dir + "/" + i for i in os.listdir(self.dir) if i!="detail.record"]

        ignore_order = tf.data.Options()
        ignore_order.experimental_deterministic = False  # disable order, increase speed
        dataset = tf.data.TFRecordDataset(
            filenames, compression_type="GZIP"
        )  # automatically interleaves reads from multiple files
        dataset = dataset.with_options(
            ignore_order
        )  # uses data as soon as it streams in, rather than in its original order
        dataset = dataset.map(
            partial(self.lecture_img), num_parallel_calls=AUTOTUNE
        )

        return dataset.batch(BATCH_SIZE)

    def load_classique(dir:str):
        """
        Load dataset original way
        """

        df=[]
        for file in [i for i in os.listdir(dir) if i!="detail.record"]:
            df.append(cv2.imread(dir + "/" + file))
        return df


class Displayer:
    """
    Permet de mieux voir l'intérieur du Dataset
    """

    def __init__(self, dataset) -> None:
        self.dataset = dataset

    def show_img(self, num_batch=1):
        """
        Montre un batch
        """

        for elem in self.dataset.take(num_batch):
            for im in elem:
                plt.imshow(im)
                plt.show()