import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy.editor as mp
from dotenv import load_dotenv
import speech_recognition as sr


def cut_and_save(movie_path, start, end, target_name):
    return ffmpeg_extract_subclip(movie_path, start, end, targetname=target_name)


def import_as_clip(path_to_video):
    return mp.VideoFileClip(path_to_video)


def separate_voice_and_music(file):
    os.system('spleeter separate -o ../../../ -f "{instrument}/{filename}.{codec}" ' + file)


def decode_speech(wave_file, start_time=None, end_time=None, language="en-US"):
    r = sr.Recognizer()
    # r.pause_threshold = 3
    # r.dynamic_energy_adjustment_damping = 0.5

    with sr.WavFile(wave_file) as source:
        if start_time is None and end_time is None:
            audio_text = r.record(source)
        else:
            audio_text = r.record(source, duration=end_time - start_time, offset=start_time)

        # recognize_() method will throw a request error if the API is unreachable, hence using exception handling
        try:
            # using google speech recognition
            text = r.recognize_google(audio_text, language=language)
            print('Converting audio transcripts into text ...')
            return text

        except:
            print('Sorry.. run again...')


if __name__ == '__main__':
    load_dotenv()

    path_to_full_movie = os.getenv("path_to_full_movie", "./")
    path_to_extract = os.getenv("path_to_extract", "./")
    path_to_trailer = os.getenv("path_to_trailer", "./")

    separate_voice_and_music(path_to_extract)

    # cut_and_save(path_to_full_movie, 2115, 2491, path_to_extract)

    # my_clip = import_as_clip(path_to_extract)
