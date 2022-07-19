import os
from pytube import YouTube
from pytube import Channel

class Extract_Video_YT:

    def __init__(self, youtube_link:str, output_dir="video/") -> None:
        self.yl = youtube_link
        self.output_dir = output_dir

    def _create_archi(self):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    def download_video(self):
        yt = YouTube(self.youtube_link)
        self._create_archi()
        yt.streams.filter(progressive=True, file_extension='mp4').first().download(self.output_dir)

    def download_channel(self):
        ch = Channel(self.yl)
        for video in ch.videos:
            print(video.length)
            print(video.keywords)
            print(video.vid_info)
            #video.streams.filter(progressive=True, file_extension='mp4').first().download(self.output_dir)

if __name__=="__main__":
    extractor = Extract_Video_YT("https://www.youtube.com/c/LesDuosImpossiblesdeJ%C3%A9r%C3%A9myFerrari")
    extractor.download_channel()