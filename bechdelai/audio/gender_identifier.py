import pandas as pd
import speech_recognition as sr
from dotenv import load_dotenv
from inaSpeechSegmenter import Segmenter


class GenderAudioIdentifier:
    def __init__(self, path_to_file, path_to_audio):
        self.title = path_to_file.split(sep='\\')[-1].split(sep='.')[0]
        self.media = path_to_file
        self.audio = path_to_audio
        self.gendered_audio_seg = self.segment()  # Dataframe
        self.dialogues = self.run_speech_to_text()
        self.speaking_time = self.compute_speaking_time_allocation()

    def __str__(self):
        return "Film : {}".format(self.title)

    def __repr__(self):
        return self.title

    def segment(self):
        seg = Segmenter(vad_engine='sm', energy_ratio=0.05)
        # energy ratio : the higher, the more selective ; vad_engine : works better with sm than smn
        segment = seg(self.media)
        return pd.DataFrame(list(filter(lambda x: x[0] == 'male' or x[0] == 'female', segment)),
                            columns=['gender', 'start', 'end'])

    def search_gender_tag(self, time: int):  # Give a time in seconds
        gender = None
        if time > self.gendered_audio_seg['end'].tail(1).item():
            return None
        for i in self.gendered_audio_seg.index:
            if time > self.gendered_audio_seg['start'][i]:
                if time < self.gendered_audio_seg['end'][i]:
                    gender = self.gendered_audio_seg['gender'][i]
                if time > self.gendered_audio_seg['end'][i]:
                    pass
        return gender

    def compute_speaking_time_allocation(self):
        speaking_time = {'male': 0, 'female': 0}
        dif = pd.Series(self.gendered_audio_seg['end'] - self.gendered_audio_seg['start'], name='time_frame')
        totaldf = pd.concat([self.gendered_audio_seg['gender'], dif], axis=1)
        for i in totaldf.index:
            if totaldf['gender'][i] == 'male':
                speaking_time['male'] += float(totaldf['time_frame'][i])
            if totaldf['gender'][i] == 'female':
                speaking_time['female'] += float(totaldf['time_frame'][i])
        return speaking_time

    def decode_speech(self, start_time=None, end_time=None, language="en-US"):
        r = sr.Recognizer()
        # r.pause_threshold = 3
        # r.dynamic_energy_adjustment_damping = 0.5
        # language can be "fr-FR"

        with sr.WavFile(self.audio) as source:
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

    def run_speech_to_text(self):
        transcript = []
        for i in self.gendered_audio_seg.index:
            transcript.append(self.decode_speech(start_time=self.gendered_audio_seg['start'][i],
                                                 end_time=self.gendered_audio_seg['end'][i],
                                                 language='fr-FR'))
        transcription = pd.concat([self.gendered_audio_seg['gender'], pd.Series(transcript, name="transcription")],
                                  axis=1)
        return transcription

    def export_to_csv(self, file_path: str):
        result = pd.concat([self.gendered_audio_seg, self.dialogues['transcription']], axis=1)
        result.to_csv(path_or_buf=file_path, sep=";", header=True, index=False)