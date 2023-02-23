from abc import ABC, abstractmethod


class DialogueTagger(ABC):
    """Abstract Class common to every gender segmentor.
    Convert an audio file to a dataframe of time slots associated with the speaker's gender.
    """
    @abstractmethod
    def extract_dialogues_subsets(self, segments_dataframe):
        pass


class RuleBasedTagger(DialogueTagger):
    def __init__(self):
        pass

    def extract_dialogues_subsets(self, segments_dataframe):
        return segments_dataframe
