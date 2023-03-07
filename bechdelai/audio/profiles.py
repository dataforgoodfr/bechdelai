""" Profiles are used to set the adapted configuration to analyse the video of interest.
"""
from abc import ABC, abstractmethod

from . import transcriber, gender_segmenter, dialogue_tagger


class Profiles(ABC):
    @abstractmethod
    def get_gender_segmentor(self):
        raise "Gender Segmentor not implemented"

    @abstractmethod
    def get_dialogue_tagger(self):
        raise "Dialogue tagger not implemented"

    @abstractmethod
    def get_transcriber(self):
        raise "Transcriber not implemented"


class French(Profiles):
    def get_gender_segmentor(self):
        return gender_segmenter.InaSpeechSegmentor()

    def get_dialogue_tagger(self):
        return dialogue_tagger.RuleBasedTagger()

    def get_transcriber(self):
        return transcriber.GoogleSpeechRecognition("fr-FR")


class USEnglish(Profiles):
    def get_gender_segmentor(self):
        return gender_segmenter.InaSpeechSegmentor()

    def get_dialogue_tagger(self):
        return dialogue_tagger.RuleBasedTagger()

    def get_transcriber(self):
        return transcriber.GoogleSpeechRecognition("en-US")
