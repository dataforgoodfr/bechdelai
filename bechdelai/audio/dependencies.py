import transcriber
import gender_segmenter
import dialogue_tagger


def get_gender_segmentor():
    return gender_segmenter.InaSpeechSegmentor()


def get_dialogue_tagger():
    return dialogue_tagger.RuleBasedTagger()


def get_gender_transcriber():
    return transcriber.GoogleSpeechRecognition()
