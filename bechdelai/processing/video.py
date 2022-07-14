from fileinput import filename
import os
import math
import cv2
import numpy as np
import tensorflow as tf
from functools import partial
from tensorflow.train import Features, Example, Feature
from tqdm import trange
import matplotlib.pyplot as plt

BATCH_SIZE = 5
AUTOTUNE = tf.data.AUTOTUNE

def extract_frames_from_videos(path,folder = ".",frame_rate = 5, optim=True):

    #Create folder if doesn't exist
    if not os.path.exists(folder):
        os.mkdir(folder)

    count = 0
    cap = cv2.VideoCapture(path) # capturing the video from the given path
    frameRate = cap.get(frame_rate) # frame rate
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Define the number of frames

    for _ in trange(length, bar_format = "{desc}: {percentage:.3f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}"):

        frameId = cap.get(1) # current frame number
        ret, frame = cap.read()
        if (ret != True):
            break

        if frame_rate == 1 or (frameId % math.floor(frameRate) == 0):
            if not optim:
                filename = os.path.join(folder,f"frame{count}.jpg")
                cv2.imwrite(filename, frame)
                
            else:
                create_tfrecord(frame, folder + "/" + str(frameId) + ".tfrecord")

            count +=1
            
    cap.release()
    print("Done!")


def create_tfrecord(frame, name):

    byte_list = tf.train.BytesList(value=[tf.io.encode_jpeg(frame).numpy()])
    person_example = Example(
        features = Features(
            feature = {
                "image": Feature(bytes_list = byte_list),
            }
        )
    )

    option = tf.io.TFRecordOptions(compression_type="GZIP")
    with tf.io.TFRecordWriter(name, option) as f:
        f.write(person_example.SerializeToString())

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