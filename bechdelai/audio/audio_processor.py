import main
import pandas as pd


class AudioProcessor:
    """Computes complete pipeline from audio to text format dialogues

    """
    def __init__(self, audio_file="", language="en-US"):
        self.audio = audio_file
        self.language = language
        self.gendered_audio_seg = self.gender_segmentor()
        self.feminine_dialogues = self.dialogue_tagger()
        self.result = self.run_speech_to_text()

    def gender_segmentor(self):
        return main.gender_segmentor.segment(self.audio)

    def dialogue_tagger(self):
        return main.dialogue_tagger.extract_dialogues_subsets(self.gendered_audio_seg)

    def run_speech_to_text(self):
        transcript = []
        for i in self.feminine_dialogues.index:
            duration = self.feminine_dialogues['end'][i] - self.feminine_dialogues['start'][i]
            transcript.append(main.stt_transcriber.speech_to_text(self.audio,
                                                                  start_time=self.gendered_audio_seg['start'][i],
                                                                  duration=duration,
                                                                  language=self.language))
        transcription = pd.concat([self.gendered_audio_seg['gender'], pd.Series(transcript, name="transcription")],
                                  axis=1)
        return transcription

    def export_to_csv(self, file_path: str):
        result = pd.concat([self.gendered_audio_seg, self.result['transcription']], axis=1)
        result.to_csv(path_or_buf=file_path, sep=";", header=True, index=False)
