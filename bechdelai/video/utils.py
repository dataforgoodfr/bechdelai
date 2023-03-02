import math
import os
from typing import List, Union

import cv2
import matplotlib.pyplot as plt
import moviepy.editor
import numpy as np
import pandas as pd
from PIL import Image
from scenedetect import ContentDetector, SceneManager, detect, open_video
from scenedetect.backends import VideoCaptureAdapter
from tqdm.auto import tqdm


def cv2_to_PIL(frame):
    return Image.fromarray(frame[:, :, [2, 1, 0]])


def get_frame_from_cap(cap, frame_id):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
    ret, frame = cap.read()
    frame = cv2_to_PIL(frame)
    return frame


def _load_video_cv2(video_path):
    cap = cv2.VideoCapture(video_path)
    return cap


def load_video(video):
    # Either a cv2 capture cap or a string for a file to open with opencv2
    if not isinstance(video, str):
        cap = video
    else:
        path = video
        if not os.path.exists(path):
            raise Exception(f"Warning the file at path '{path}' does not exist")
        cap = _load_video_cv2(path)
    return cap


def extract_frames_from_video(
    video,
    folder=".",
    fps=1,
    save=False,
    max_seconds=None,
    frame_start=0,
    frame_end=None,
    show_progress=False,
):
    """
    From https://www.analyticsvidhya.com/blog/2018/09/deep-learning-video-classification-python/?utm_campaign=News&utm_medium=Community&utm_source=DataCamp.com

    TODO:
    - Add progressbar
    - Size how long it will take
    - Change the frame rate as variable
    - Make it not mandatory to save as file but also in memory

    """

    # Prepare frames
    frames = []
    count = 0

    # Either a cv2 capture cap or a string for a file to open with opencv2
    cap = load_video(video)

    if save:
        if not os.path.exists(folder):
            os.mkdir(folder)

    # Get frames per second and frame rate
    real_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_ratio = int(real_fps / fps)
    assert fps <= real_fps

    # Get total frames
    n_frames_total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    n_frames_final = int(n_frames_total // frame_ratio) + 1

    # Start video at given frame id
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_start)
    start_time = frame_start / real_fps

    with tqdm(total=n_frames_final, display=show_progress) as pbar:
        while cap.isOpened():
            # Get current frame
            frame_id = cap.get(1)  # current frame number
            ret, frame = cap.read()

            # Calculate current time
            current_time = frame_id / real_fps

            # Stop if stream is finished (went through all the frames)
            if ret != True:
                print("Video is finished")
                break

            # Stop if above max seconds
            if max_seconds is not None:
                if (current_time - start_time) > max_seconds:
                    print(f"Stopped after {max_seconds} seconds")
                    break

            # Stop if above max frame id
            if frame_end is not None:
                if frame_id >= frame_end:
                    break

            # Record frame at given frame rate
            if frame_id % math.floor(frame_ratio) == 0:
                # Save image as file
                if save:
                    filename = os.path.join(folder, f"frame{count}.jpg")
                    count += 1
                    cv2.imwrite(filename, frame)

                # Or save image in memory as PIL image
                else:
                    frame_pil = cv2_to_PIL(frame)
                    frames.append(frame_pil)
                pbar.update(1)
    # cap.release()

    if save:
        print("Done!")
    else:
        return cap, frames


def show_frames(frames, columns=6, figsize_row=(15, 1), titles=None):
    rows = (len(frames) // columns) + 1

    for row in range(rows):
        fig = plt.figure(figsize=figsize_row)
        remaining_columns = len(frames) - (row * columns)
        row_columns = columns if remaining_columns > columns else remaining_columns
        for column in range(row_columns):
            try:
                img = frames[row * columns + column].array
            except:
                img = np.array(frames[row * columns + column])
            fig.add_subplot(1, columns, column + 1)
            plt.axis("off")
            plt.imshow(img)
            if titles is not None:
                plt.title(titles[row * columns + column])
        plt.show()


def detect_scenes(cap, threshold=27.0, show_progress=False):
    # Convert cv2 capture to video
    video = VideoCaptureAdapter(cap)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))

    # Detect all scenes in video from current position to end.
    scene_manager.detect_scenes(video, show_progress=show_progress)

    # Detect all scenes
    scene_list = scene_manager.get_scene_list()
    return scene_list


class Scene:
    def __init__(self, start, end=None):
        if end is None:
            self.start = start[0]
            self.end = start[1]
        else:
            self.start = start
            self.end = end

    @property
    def frames(self):
        return self.start.get_frames(), self.end.get_frames()

    @property
    def n_frames(self):
        return self.end.get_frames() - self.start.get_frames()

    @property
    def duration(self):
        return self.end.get_seconds() - self.start.get_seconds()

    def get_duration(self):
        return f"{self.duration:.2f}s"

    @property
    def timecodes(self):
        return self.start.get_timecode(), self.end.get_timecode()

    def __repr__(self):
        timecodes = self.timecodes
        return f"Scene({timecodes[0].replace('00:','')}->{timecodes[1].replace('00:','')},duration={self.duration:.2f},n={self.n_frames})"


def extract_frames_from_scenes(
    video, threshold=27.0, show_progress=False, method="middle"
):
    assert method in ["first", "last", "middle"]

    # Prepare frames
    frames = []
    count = 0

    # Either a cv2 capture cap or a string for a file to open with opencv2
    cap = load_video(video)

    # Detect scene list
    scene_list = detect_scenes(cap, threshold=threshold, show_progress=show_progress)
    n_scenes = len(scene_list)
    print(f"Detected {n_scenes} scenes in the video")

    # Get middle image for each scene
    # Sometimes first and last images are still transitions
    # TODO :
    # - get more images from each scene
    # - get n images equireparties dans chaque scene

    for i, scene in enumerate(tqdm(scene_list, display=show_progress)):
        # Get frame ids boundaries
        frame_start, frame_end = scene[0].get_frames(), scene[1].get_frames()

        # Find frame_id to extract
        if method == "first":
            frame_to_select = frame_start
        elif method == "last":
            frame_to_select = frame_end
        else:
            frame_to_select = frame_start + (frame_end - frame_start) // 2

        # Get frames in the sequence
        frame = get_frame_from_cap(cap, frame_to_select)
        frames.append(frame)

    # Add duration for each scene
    scene_list = [Scene(scene) for scene in scene_list]

    return cap, frames, scene_list


MoviePyTimestamp = Union[float, List[float], str]


def subclip_video(
    fname: str, start_time: MoviePyTimestamp, end_time: MoviePyTimestamp
) -> moviepy.editor.VideoFileClip:
    clip = moviepy.editor.VideoFileClip(fname)
    return clip.subclip(start_time, end_time)
