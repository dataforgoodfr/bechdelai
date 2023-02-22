from abc import ABC, abstractmethod
import speech_recognition as sr


class Transcriber(ABC):
    # Abstract Class common to every transcriber model.
    # Possibility to deal with audio ranges of a certain duration.
    def __init__(self):
        self.r = sr.Recognizer()

    def read(self, audio_file):
        with sr.AudioFile(audio_file) as source:
            return self.r.record(source)

    @abstractmethod
    def speech_to_text(self, audio_file):
        pass


class GoogleSpeechRecognition(Transcriber):
    # Recognize speech using Google Speech Recognition
    # Can be improved by adding language choice
    def __init__(self):
        super().__init__()

    def speech_to_text(self, audio_file):
        audio = self.read(audio_file)
        try:
            return self.r.recognize_google(audio)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
