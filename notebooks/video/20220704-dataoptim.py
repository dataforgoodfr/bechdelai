import sys
sys.path.append('/home/virgaux/dataforgood/bechdelai/bechdelai')
import processing.extract_img
import processing.load_img


#processing.extract_img.extract_frames_from_videos("video/The Gunfighter (Best Short Film Ever).mp4", "monfilmv2", optim=True)
dataset = processing.load_img.load_dataset("monfilmv2")
processing.load_img.show_img(dataset)