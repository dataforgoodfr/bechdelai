from abc import ABC, abstractmethod
import speech_recognition as sr


class Transcriber(ABC):
    # Abstract Class common to every transcriber model.
    # Possibility to deal with audio ranges of a certain duration.
    def __init__(self):
        self.r = sr.Recognizer()

    def read(self, audio_file, start_time=None, duration=None):
        with sr.AudioFile(audio_file) as source:
            return self.r.record(source, duration=duration, offset=start_time)

    @abstractmethod
    def speech_to_text(self, audio_file, start_time, duration, language):
        pass


class GoogleSpeechRecognition(Transcriber):
    # Recognize speech using Google Speech Recognition
    # Can be improved by adding language choice
    def __init__(self):
        super().__init__()

    def speech_to_text(self, audio_file, start_time, duration, language):
        audio = self.read(audio_file, start_time, duration)
        try:
            return self.r.recognize_google(audio, language=language)  # It may be necessary to change the API key
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
