import os

import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def cut_and_save(movie_path: str, start: float, end: float, target_name: str) -> None:
    """This function cuts a video from the start to the end time and saves it as target_name.

    Args:
        movie_path (str): The path to the video file.
        start (float): The start time in seconds.
        end (float): The end time in seconds.
        target_name (str): The file name of the new video file.

    Returns:
        None
    """
    return ffmpeg_extract_subclip(movie_path, start, end, targetname=target_name)


def import_as_clip(path_to_video: str) -> mp.VideoFileClip:
    """Imports a video file as a VideoFileClip object.
    
    Args:
        path_to_video (str): Path to a video file.
    
    Returns:
        mp.VideoFileClip: VideoFileClip object.
    """
    return mp.VideoFileClip(path_to_video)


# Splits a file into its individual parts using spleeter
# Does not work above 700 seconds
def separate_voice_and_music(file: str) -> None:  # Do not work above 700 seconds
    os.system('spleeter separate -d 700.0 -o ../../../ -f "{instrument}/{filename}.{codec}" ' + file)


def extract_audio_from_movie(file: str, extension: str = '.wav') -> None:
    """Extract the audio from a movie and save it to a file.
    
    The audio is saved in the same directory as the movie.
    
    Args:
        file (str): The name of the movie file to extract the audio from.
        extension (str): The file extension of the audio file to save.
    """
    clip = import_as_clip(file)
    clip.audio.write_audiofile(file.split(sep='.')[0] + extension)