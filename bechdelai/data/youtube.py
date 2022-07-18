import os

class Extract_Video_YT:

    def __init__(self, youtube_link:str, output_dir="video/") -> None:
        self.yl = youtube_link
        self.output_dir = output_dir

    def _create_archi(self):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    def download_video(self):
        self._create_archi()
        os.system("yt-dlp -f mp4 " + self.yl + " -o " + self.output_dir + "/ma_vid.mp4")


if __name__=="__main__":
    extractor = Extract_Video_YT("https://www.youtube.com/watch?v=INwb2Avrdqo")
    extractor.download_video()