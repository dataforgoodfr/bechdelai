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

    def load_dataset(self):
        """
        Charger les données
        """

        filenames = [self.dir + "/" + i for i in os.listdir(self.dir)]

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
        for file in os.listdir(dir):
            df.append(cv2.imread(dir + "/" + file))
        return df

class Displayer:

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