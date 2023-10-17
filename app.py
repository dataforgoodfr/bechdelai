# Inspired from https://huggingface.co/spaces/vumichien/whisper-speaker-diarization/blob/main/app.py

import gradio as gr
import re
import time
import os 

import pandas as pd
import numpy as np
import sys
sys.path.append("../../")

from pytube import YouTube

# Custom code
from bechdelai.data.youtube import download_youtube_video
from bechdelai.audio.utils import extract_audio_from_video
from bechdelai.audio.gender_segmenter import InaSpeechSegmentor
from bechdelai.audio.transcriber import WhisperAPI
from bechdelai.nlp.gpt import GPT3

# Constants
# whisper_models = ["tiny.en","base.en","tiny","base", "small", "medium", "large"]
# device = 0 if torch.cuda.is_available() else "cpu"
# os.makedirs('output', exist_ok=True)

def get_youtube(video_url):
    yt = YouTube(video_url)
    abs_video_path = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
    print("Success download video")
    print(abs_video_path)
    return abs_video_path


def speech_to_text(video_filepath, selected_source_lang = "en", whisper_model = "tiny.en"):
    """
    # Transcribe youtube link using OpenAI Whisper
    1. Using Open AI's Whisper model to seperate audio into segments and generate transcripts.
    2. Generating speaker embeddings for each segments.
    3. Applying agglomerative clustering on the embeddings to identify the speaker for each segment.
    
    Speech Recognition is based on models from OpenAI Whisper https://github.com/openai/whisper
    Speaker diarization model and pipeline from by https://github.com/pyannote/pyannote-audio
    """
    
    whisper_api = WhisperAPI()
    gender = InaSpeechSegmentor(only_gender=True,batch_size = 32)

    # Convert video to audio
    audio_filepath = extract_audio_from_video(video_filepath,"mp3")
    result,segments,text = whisper_api.speech_to_text(audio_filepath)
    segments_ina = gender._convert_whisper_output(segments)
    segments_ina = gender.predict_gender_on_segments(audio_filepath,segments_ina)
    segments_with_gender = segments.merge(segments_ina[["gender","start"]],on = "start",how = "left")

    dialogue_id = segments_with_gender["speech"].astype(int).diff(1).fillna(0)
    dialogue_id.loc[dialogue_id < 0] = 0
    segments_with_gender["dialogue_id"] = dialogue_id.cumsum()
    segments_with_gender.loc[segments_with_gender["speech"] == False,"dialogue_id"] = np.NaN

    return [segments_with_gender,text]

source_language_list = ["en","fr"]

# ---- Gradio Layout -----
# Inspiration from https://huggingface.co/spaces/RASMUS/Whisper-youtube-crosslingual-subtitles
video_in = gr.Video(label="Video file", mirror_webcam=False)
youtube_url_in = gr.Textbox(label="Youtube url", lines=1, interactive=True)
# selected_source_lang = gr.Dropdown(choices=source_language_list, type="value", value="en", label="Spoken language in video", interactive=True)
# selected_whisper_model = gr.Dropdown(choices=whisper_models, type="value", value="tiny.en", label="Selected Whisper model", interactive=True)
df_init = pd.DataFrame(columns=['start', 'end', 'text', 'speech', 'gender', 'duration', 'dialogue_id'])
transcription_df = gr.DataFrame(value = df_init,label="Répartition du temps de parole", row_count=(0, "dynamic"), max_rows = 25, wrap=True, overflow_row_behaviour='paginate')
output_text = gr.Textbox(label = "Transcribed text",lines = 10)

title = "BechdelAI - demo"
demo = gr.Blocks(title=title,live = True)
demo.encrypt = False


with demo:
    with gr.Tab("BechdelAI - dialogue demo"):
        gr.Markdown('''
            <div>
                <h1 style='text-align: center'>BechdelAI - Dialogue demo</h1>
            </div>
        ''')

        with gr.Row():
            gr.Markdown('''# 🎥 Download Youtube video''')
              

        with gr.Row():

            with gr.Column():
                # gr.Markdown('''### You can test by following examples:''')
                examples = gr.Examples(examples=
                        [
                        "https://www.youtube.com/watch?v=FDFdroN7d0w",
                        "https://www.youtube.com/watch?v=b2f2Kqt_KcE",
                        "https://www.youtube.com/watch?v=ba5F8G778C0",
                    ],
                    label="Examples", inputs=[youtube_url_in])
                youtube_url_in.render()
                download_youtube_btn = gr.Button("Download Youtube video")
                download_youtube_btn.click(get_youtube, [youtube_url_in], [
                    video_in])
                print(video_in)
                
            with gr.Column():
                video_in.render()

        with gr.Row():
            gr.Markdown('''# 🎙 Extract text from video''')

        with gr.Row():
            with gr.Column():
                transcribe_btn = gr.Button("Transcribe audio and diarization")
                # transcribe_btn.click(speech_to_text, [video_in, selected_source_lang, selected_whisper_model], [transcription_df,output_text])
                transcribe_btn.click(speech_to_text, [video_in], [transcription_df,output_text])
            with gr.Column():
                output_text.render()
        with gr.Row():
            transcription_df.render()

demo.launch(debug=True)