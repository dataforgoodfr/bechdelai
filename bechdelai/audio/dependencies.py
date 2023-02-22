import transcriber


def get_gender_transcriber():
    return transcriber.GoogleSpeechRecognition()
