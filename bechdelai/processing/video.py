
import os
import math
import cv2


def extract_frames_from_videos(path,folder = "."):
    """
    From https://www.analyticsvidhya.com/blog/2018/09/deep-learning-video-classification-python/?utm_campaign=News&utm_medium=Community&utm_source=DataCamp.com

    TODO:
    - Add progressbar
    - Size how long it will take
    - Change the frame rate as variable
    - Make it not mandatory to save as file but also in memory 

    """

    if not os.path.exists(folder):
        os.mkdir(folder)

    count = 0
    cap = cv2.VideoCapture(path)   # capturing the video from the given path
    frameRate = cap.get(5) #frame rate
    x=1
    while(cap.isOpened()):
        frameId = cap.get(1) #current frame number
        ret, frame = cap.read()
        if (ret != True):
            break
        if (frameId % math.floor(frameRate) == 0):
            filename = os.path.join(folder,f"frame{count}.jpg")
            count +=1
            cv2.imwrite(filename, frame)
    cap.release()
    print("Done!")