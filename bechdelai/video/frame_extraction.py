
import os
import math
import cv2
from tqdm.auto import tqdm
from PIL import Image

def extract_frames_from_videos(path,folder = ".",frame_rate = 5,save = True,max_seconds = None):
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

    if not os.path.exists(path):
        raise Exception(f"Warning the file at path '{path}' does not exist")

    if save:
        if not os.path.exists(folder):
            os.mkdir(folder)

    count = 0
    cap = cv2.VideoCapture(path)   # capturing the video from the given path

    # Get frames per second and frame rate 
    fps = cap.get(cv2.CAP_PROP_FPS)
    final_frame_rate = int(fps / frame_rate)

    # Get total frames
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    final_total_frames = int((total_frames // final_frame_rate) + 1)

    with tqdm(total = final_total_frames) as pbar:
        while(cap.isOpened()):

            # Get current frame
            frameId = cap.get(1) #current frame number
            ret, frame = cap.read()

            # Stop if stream is finished (went through all the frames)
            if (ret != True):
                break

            # Stop if above max seconds
            if max_seconds is not None:
                if frameId / fps > max_seconds:
                    print(f"Stopped at {max_seconds} seconds")
                    break 

            # Record frame at given frame rate
            if frameId % math.floor(final_frame_rate) == 0:
                # print(frameId)

                # Save image as file
                if save:
                    filename = os.path.join(folder,f"frame{count}.jpg")
                    count +=1
                    cv2.imwrite(filename, frame)

                # Or save image in memory as PIL image
                else:
                    frame_pil = Image.fromarray(frame[:,:,[2,1,0]])
                    frames.append(frame_pil)
                pbar.update(1)
    cap.release()
     
    if save:
        print("Done!")
    else:
        return frames

