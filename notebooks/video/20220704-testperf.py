import sys
import time
sys.path.append('/home/virgaux/dataforgood/bechdelai/bechdelai')
import processing.extract_img
import processing.load_img


def test_capture_original():
    processing.extract_img.extract_frames_from_videos("video/longue_video.mp4", "monfilm", optim=False)

def test_capture_optim():
    processing.extract_img.extract_frames_from_videos("video/longue_video.mp4", "monfilm", optim=True)

def test_load_dataset():
    return processing.load_img.load_dataset("monfilm")

def test_load_classic():
    return processing.load_img.load_classique("monfilm")

"""
start_time = time.time()
test_capture_original()
test_load_classic()
shutil.rmtree("monfilm")
print("--- %s seconds ---" % (time.time() - start_time))
"""


start_time = time.time()
test_capture_optim()
dataset = test_load_dataset()
print("--- %s seconds ---" % (time.time() - start_time))

#shutil.rmtree("monfilm")


#Show images
processing.load_img.show_img(dataset)