import os
import moviepy.editor as mp
from dotenv import load_dotenv
import speech_recognition as sr
from inaSpeechSegmenter import Segmenter
from inaSpeechSegmenter.export_funcs import seg2csv, seg2textgrid


load_dotenv()

path_to_video = os.getenv("path_to_video", "./")
my_clip = mp.VideoFileClip(path_to_video)


def decodeSpeech(wavefile, start_time=None, end_time=None, language=None):
    r = sr.Recognizer()
    # r.pause_threshold = 3
    # r.dynamic_energy_adjustment_damping = 0.5

    with sr.WavFile(wavefile) as source:
        if start_time == None and end_time == None:
            audio_text = r.record(source)
        else:
            audio_text = r.record(source, duration=end_time - start_time, offset=start_time)

    if language == None:  # default language is American English
        lg = "en-US"
    else:
        lg = language

        # recoginize_() method will throw a request error if the API is unreachable, hence using exception handling
        try:

            # using google speech recognition
            text = r.recognize_google(audio_text, language=lg)
            print('Converting audio transcripts into text ...')
            return text

        except:
            print('Sorry.. run again...')

seg = Segmenter()
# segmentation = seg(my_clip.audio)
# print(segmentation)


# cap = cv2.VideoCapture(path_to_video)
# while(cap.isOpened()):
#     ret, frame = cap.read()
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     cv2.imshow('frame', gray)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cap.release()
# cv2.destroyAllWindows()

