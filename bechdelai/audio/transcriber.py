import os
import pandas as pd
import speech_recognition as sr
import openai
import whisper
from dotenv import load_dotenv
from abc import ABC, abstractmethod


class Transcriber(ABC):
    # Abstract Class common to every transcriber model.
    # Possibility to deal with audio ranges of a certain duration.
    def __init__(self):
        pass

    @abstractmethod
    def speech_to_text(self, audio_file, start_time, duration):
        pass


class GoogleSpeechRecognition(Transcriber):
    # Recognize speech using Google Speech Recognition
    def __init__(self, language):
        self.language = language
        self.r = sr.Recognizer()

    def read(self, audio_file, start_time=None, duration=None):
        with sr.AudioFile(audio_file) as source:
            return self.r.record(source, duration=duration, offset=start_time)

    def speech_to_text(self, audio_file, start_time, duration):
        audio = self.read(audio_file, start_time-1, duration+2)
        try:
            return self.r.recognize_google(audio, language=self.language)  # It may be necessary to change the API key
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))


class WhisperAPI(Transcriber):
    def __init__(self,api_key = None):

        # Set up API key
        if api_key is None:
            try:
                load_dotenv()
                api_key = os.environ["OPENAI_API_KEY"]
            except:
                raise Exception("No OpenAI key was found in the environment or in a .env file")

        assert api_key.startswith("sk-")
        openai.api_key = api_key

    def speech_to_text(self,audio_file,response_format = "verbose_json"):
        # From https://openai.com/blog/introducing-chatgpt-and-whisper-apis
        # Doc at https://platform.openai.com/docs/guides/speech-to-text
        # TODO should add test if file > 25mb -> fails with openAI API, use mp3 and not wav as safety check
        file = open(audio_file, "rb")
        result = openai.Audio.transcribe("whisper-1", file,response_format = response_format)
        segments = pd.DataFrame([dict(x) for x in result["segments"]])[["start","end","text"]]
        segments["text"] = segments["text"].str.strip()
        segments["speech"] = segments["text"].map(lambda x : x != "♪♪")
        text = result["text"]
        return result,segments,text


class Whisper(Transcriber):
    def __init__(self,model_name = "tiny.en"):
        assert model_name in ["tiny.en","base.en","tiny","base", "small", "medium", "large"]
        self.model = whisper.load_model(model_name)

    def speech_to_text(self,audio_file,language = "en"):

        options = dict(language=language, beam_size=5, best_of=5)
        transcribe_options = dict(task="transcribe", **options)
        result = self.model.transcribe(audio_file, **transcribe_options)
        segments = result["segments"]
        text = result["text"].strip()

        return result,segments,text

