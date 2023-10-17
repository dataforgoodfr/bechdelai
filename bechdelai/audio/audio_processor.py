import pandas as pd


class AudioProcessor:
    """Computes complete pipeline from audio to text format dialogues
    gendered_audio_seg represents gender identification + voice activity detection
    feminine_dialogues aims to keep only dialogues where women are speaking
    result transforms selected audios into text
    """
    def __init__(self, config, audio_file=""):
        self.audio = audio_file
        self.config = config
        self.gendered_audio_seg = self.gender_segmentor()
        self.feminine_dialogues = self.dialogue_tagger()
        self.result = self.run_speech_to_text()

    def gender_segmentor(self):
        return self.config.get_profile().get_gender_segmentor().segment(self.audio)

    def dialogue_tagger(self):
        return self.config.get_profile().get_dialogue_tagger().extract_dialogues_subsets(self.gendered_audio_seg)

    def run_speech_to_text(self):
        transcript = []
        for i in self.feminine_dialogues.index:
            duration = self.feminine_dialogues['end'][i] - self.feminine_dialogues['start'][i]
            transcript.append(self.config.get_profile().get_transcriber().speech_to_text(self.audio,
                                                                                         self.gendered_audio_seg['start'][i],
                                                                                         duration))
        transcription = pd.concat([self.gendered_audio_seg['gender'], pd.Series(transcript, name="transcription")],
                                  axis=1)
        return transcription

    def full_dataframe(self):
        return pd.concat([self.gendered_audio_seg, self.result['transcription']], axis=1)

    def export_to_csv(self, file_path: str):
        result = self.full_dataframe()
        result.to_csv(path_or_buf=file_path, sep=";", header=True, index=False, encoding="utf-8")
