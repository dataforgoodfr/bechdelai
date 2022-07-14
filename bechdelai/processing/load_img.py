import tensorflow as tf
import cv2
import os
import matplotlib.pyplot as plt
from functools import partial
import numpy as np

BATCH_SIZE = 5
AUTOTUNE = tf.data.AUTOTUNE


def lecture_img(example):
    """
    Permet de lire une image et la décoder pour passer de bytes à jpeg
    """

    image_feature_description = {  
        'image': tf.io.FixedLenFeature([], tf.string),  
    }
    example = tf.io.parse_single_example(example, image_feature_description)
    img = tf.cast(example["image"], tf.string)

    return tf.io.decode_jpeg(img, channels=3)

def preprocessing_minimal(dataset, dir:str):
    """
    Nettoie les images en vu d'une tâche
    """

    li = []
    dataset_iter = iter(dataset)
    for _ in range(len(os.listdir(dir))):
        li.append(np.array(cv2.cvtColor(next(dataset_iter).numpy(), cv2.COLOR_BGR2RGB)))
    return np.array(li)


def cvt(image):
    return cv2.cvtColor(image.numpy(), cv2.COLOR_BGR2RGB)

def tf_cv2_func(image):
    image = tf.py_function(cvt, [image], [tf.int32])
    return image

def load_dataset(dir:str):
    """
    Charger les données
    """

    filenames = [dir + "/" + i for i in os.listdir(dir)]

    ignore_order = tf.data.Options()
    ignore_order.experimental_deterministic = False  # disable order, increase speed
    dataset = tf.data.TFRecordDataset(
        filenames, compression_type="GZIP"
    )  # automatically interleaves reads from multiple files
    dataset = dataset.with_options(
        ignore_order
    )  # uses data as soon as it streams in, rather than in its original order
    dataset = dataset.map(
        partial(lecture_img), num_parallel_calls=AUTOTUNE
    )

    dataset = dataset.map(
        partial(tf_cv2_func), num_parallel_calls=AUTOTUNE
    )

    # returns a dataset of (image, label) pairs if labeled=True or just images if labeled=False
    return dataset


def show_img(dataset, num_batch=1):
    """
    Montre un batch
    """

    for elem in dataset.take(num_batch):
        plt.imshow(elem[0])
        plt.show()