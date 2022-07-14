import tensorflow as tf
import cv2
import os
import matplotlib.pyplot as plt
from functools import partial
import numpy as np


BATCH_SIZE = 5
AUTOTUNE = tf.data.AUTOTUNE

def lecture_img(example):

    image_feature_description = {  
        'image': tf.io.FixedLenFeature([], tf.string),  
    }
    example = tf.io.parse_single_example(example, image_feature_description)
    img = tf.cast(example["image"], tf.string)

    return tf.io.decode_jpeg(img, channels=3)

def preprocessing(dataset, dir:str):

    li = []
    dataset_iter = iter(dataset)
    for _ in range(len(os.listdir(dir))):
        li.append(np.array(cv2.cvtColor(next(dataset_iter).numpy(), cv2.COLOR_BGR2RGB)))
    return np.array(li)

def load_dataset(dir:str):

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

    images_cvt = preprocessing(dataset, dir)

    # returns a dataset of (image, label) pairs if labeled=True or just images if labeled=False
    return tf.data.Dataset.from_tensor_slices(images_cvt).batch(BATCH_SIZE)


def show_img(dataset, num_batch=1):
    for elem in dataset.take(num_batch):
        for im in elem:
            plt.imshow(im)
            plt.show()