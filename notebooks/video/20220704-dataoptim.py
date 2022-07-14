import sys
sys.path.append('/home/virgaux/dataforgood/bechdelai/bechdelai')
import processing.video


processing.video.extract_frames_from_videos("video/The Gunfighter (Best Short Film Ever).mp4", "monfilmvnormal", optim=False)

#dataset = processing.video.load_dataset("monfilmv2")
#processing.video.show_img(dataset)