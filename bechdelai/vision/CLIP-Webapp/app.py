import pandas as pd
import streamlit as st
import os
import sys
import cv2
from deepface import DeepFace
import matplotlib.pyplot as plt
import tempfile
import cv2 as cv

sys.path.append("../../../")
from bechdelai.processing.video import extract_frames_from_videos
from bechdelai.vision.video import Video
from bechdelai.vision.clip import CLIP
from bechdelai.vision.bechdelizer import Bechdelizer


@st.cache(allow_output_mutation=True)
def load_model():
    clip = CLIP()
    return clip

def save_uploaded_file(uploaded_file):
    path_file = os.path.join("data",uploaded_file.name)
    with open(path_file,"wb") as f:
        f.write(uploaded_file.getbuffer())
    return path_file

def load_videos():
    uploaded_files = st.file_uploader("Choose a mp4 file", accept_multiple_files=False)
    if uploaded_files is not None:
        path_file = save_uploaded_file(uploaded_files)
        st.success('File saved to {}'.format(path_file))
    else:
        path_file = None
    return path_file

def intro_app():
    st.title("SIMULATEUR DU CLIP MODEL") #Affichage d'un titre
    st.header("Introduction")
    st.write("Cette Webapp a pour objectif de vous permettre de faire des simulation avec le model CLIP. \
              Le model CLIP permet de créer une série de petite phrases décrivant une scène de film et \
              de vérifier pour chacune d'entre elles si elle décrivent chaque image du film avec un coefficient.")

    st.subheader("Load a movie Trailer")
    video_path = load_videos()

    st.subheader("Configuration")
    suggestions = st.text_area("Enter your list of sentences separated by ','", height=100)
    return suggestions, video_path        

def run_clip(clip,video_path, prompts):
    st.write('Your sentences are :', prompts)
    frame_rate = 5
    image_width = 600
    extract_frames_from_videos(video_path,"tempDir/clip_frame",frame_rate = frame_rate)
    video = Video(path = "./clip_frame")
    video.resize(width = image_width)
    #Compute predictions and get plotly charts
    preds ,probas = clip.predict(video,prompts)
    return video, preds, probas


    #clip.replay(video,preds)


def show_results(video):
    images = [x.img for x in video.frames]
    images_count = len(images)
    #values = st.slider('Select the picture you want to see',0, images_count)
    #st.write(f"Image number {values} out of {images_count}")
    #st.image(images[values], f"Image number {values} out of {images_count}")
    return images, images_count

def show_preds_by_image(preds,i):
    fig, _ = plt.subplots()
    preds.iloc[i].sort_values(ascending = False).plot(kind = "bar",figsize = (15,3))
    plt.xticks(rotation=45,horizontalalignment = "right")
    plt.title(f"Labels for frame {i}")
    return fig


def replay(video, preds):
    images = [x.img for x in video.frames]
    images_count = len(images)
    images_count_range = range(images_count)
    st.write('Predictions Result')
    values = st.sidebar.selectbox('Please select the image you want to analyse',
                        images_count_range)

    #values = st.slider('Select the picture you want to see',0, images_count-1)
    st.image(images[values], f"Image {values +1} out of {images_count}")
    fig = show_preds_by_image(preds,values)
    st.pyplot(fig)


if __name__ == '__main__':
    #clip = load_model()
    suggestions, video_path = intro_app()

    Bechdelizer = Bechdelizer()
    if st.button('Submit your sentences'):
        df = Bechdelizer.women_detection_deepface(video_path = video_path,time_rate=2)
        list_suggestions = [str(s).strip() for s in suggestions.split(',')]
        if suggestions != None or len(list_suggestions) > 8:
            # video, preds, probas = run_clip(clip,video_path, list_suggestions)
            # images, images_count = show_results(video)

            #video = Video(path='./tempDir/frames')
            #video.resize(width = 600)
            #preds,probas = clip.predict(video,list_suggestions)
            #frames = [df, probas]
            #result = pd.concat(frames, axis=1)
            st.dataframe(df)
            faces = os.listdir('tempDir/frames_w_faces/') 
            if len(faces) > 0:
                for face in faces: 
                    st.image(image=face,caption="Image")
    #        replay(video, preds)
    #    else:
    #        st.markdown('**Please enter at least 8 sentences before moving forward**')

    
    #pred_fig = clip.show_preds_area(preds)
    #probas_fig = clip.show_preds_area(probas)

    #images, images_count = show_results(video)
    #values = st.slider('Select the picture you want to see',0, images_count-1)

    #st.image(images[values], f"Image {values +1} out of {images_count}")
    #st.plotly_chart(probas_fig)
    #st.plotly_chart(pred_fig)