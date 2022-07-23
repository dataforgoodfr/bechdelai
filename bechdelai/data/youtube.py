import os
import urllib
import cv2
import numpy as np
import json
from pytube import YouTube
from pytube import Channel

class Extract_Video_YT:

    def __init__(self, youtube_link:str, output_dir="/".join(os.getcwd().split("/")[:-2]) + "/data/sample_video_yt") -> None:
        self.yl = youtube_link
        self.output_dir = output_dir

    def _create_archi(self):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)

    def _get_detail(self, video)->dict:
        """
        
        """

        req = urllib.request.urlopen(video.thumbnail_url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.cvtColor(cv2.imdecode(arr, -1), cv2.COLOR_BGR2RGB)

        info_filter = {
            "author": video.author,
            "lenght": video.length,
            "title": video.title,
            "keywords": video.keywords,
            "date": video.publish_date.strftime("%m/%d/%Y"),
            "views": video.views,
            "description": video.description,
            "image_desc": img.tolist()
        }

        return info_filter

    def _writer_detail(self, detail:dict):
        with open(self.output_dir + "/" + detail["title"] + '.json', 'w', encoding='utf-8') as f:
            json.dump(detail, f, ensure_ascii=False, indent=4)

    def download_video(self, video_dl = True, with_detail=True):
        video = YouTube(self.yl)
        self._create_archi()
        if video_dl:
            video.streams.filter(progressive=True, file_extension='mp4').first().download(self.output_dir)
        if with_detail:
            detail = self._get_detail(video)
            self._writer_detail(detail)


    def download_channel(self, video_dl = True, with_detail=True):
        #TODO Vérifier que c'est bien un channel et pas une vidéo simple

        ch = Channel(self.yl)
        for video in ch.videos:
            if video_dl:
                video.streams.filter(progressive=True, file_extension='mp4').first().download(self.output_dir)
            if with_detail:
                detail = self._get_detail(video)
                self._writer_detail(detail)