import os

import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def cut_and_save(movie_path: str, start: float, end: float, target_name: str) -> None:
    """This function cuts a video from the start to the end time and saves it as target_name.

    Parameters:
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
    
    Parameters:
        path_to_video (str): Path to a video file.
    
    Returns:
        mp.VideoFileClip: VideoFileClip object.
    """
    return mp.VideoFileClip(path_to_video)




def extract_audio_from_video(file: str, extension: str = 'wav') -> None:
    """Extract the audio from a film and save it to a file.
    
    The audio is saved in the same directory as the film.
    
    Parameters:
        file (str): The name of the film file to extract the audio from.
        extension (str): The file extension of the audio file to save (default is ".wav").
    """
    assert extension in ["wav","mp3"]
    clip = import_as_clip(file)
    clip.audio.write_audiofile(f"{file.split(sep='.')[0]}.{extension}")
