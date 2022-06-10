import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy.editor as mp
from dotenv import load_dotenv


def cut_and_save(movie_path, start, end, target_name):
    return ffmpeg_extract_subclip(movie_path, start, end, targetname=target_name)


def import_as_clip(path_to_video):
    return mp.VideoFileClip(path_to_video)


def separate_voice_and_music(file):
    os.system('spleeter separate -o ../../../ -f "{instrument}/{filename}.{codec}" ' + file)


def extract_audio_from_movie(file, extension='.wav'):
    clip = import_as_clip(file)
    clip.audio.write_audiofile(file.split(sep='.')[0] + extension)


if __name__ == '__main__':
    load_dotenv()

    path_to_full_movie = os.getenv("path_to_full_movie", "./")
    path_to_extract = os.getenv("path_to_extract", "./")
    path_to_trailer = os.getenv("path_to_trailer", "./")

    extract_audio_from_movie(path_to_full_movie)
    # separate_voice_and_music(path_to_extract)

    # cut_and_save(path_to_full_movie, 2115, 2491, path_to_extract)

    # my_clip = import_as_clip(path_to_extract)
