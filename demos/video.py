import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import os
import io
import time
import json
import plotly.express as px


import bechdelai
from bechdelai.utils.video import extract_frames_from_videos
from bechdelai.vision.video import Video
from bechdelai.vision.clip import CLIP
from bechdelai.utils.timeline import convert_to_timeline,fn_timeline

st.set_page_config(page_title="BechdelAI", page_icon="🎥", layout="wide", initial_sidebar_state="auto", menu_items=None)

st.sidebar.image("demos/logo2.png")
st.sidebar.write("## Video analysis")

@st.cache(allow_output_mutation=True)
def get_video(path):
    video = Video(path = path,frame_rate = 2,max_seconds = None)
    video.resize(width = 800)
    return video

@st.cache(allow_output_mutation=True)
def get_clip():
    clip = CLIP()
    return clip


with st.sidebar.expander("Select video"):
    # File selection
    file_path = st.text_input("File path","C:\\Users\\theo.alvesdacosta\\Videos\\HP\\Harry Potter et la Coupe de Feu - Bande Annonce Officielle (VF) - Daniel Radcliffe - Emma Watson.mp4")
    if "file_path" in st.session_state:
        if st.session_state.file_path != file_path:
            st.session_state.file_path = file_path
            video = get_video(file_path)

        else:
            if "video" not in st.session_state:
                video = get_video(file_path)
                st.session_state.video = video
            else:
                video = st.session_state.video
    else:
        if "video" not in st.session_state:
            video = get_video(file_path)
            st.session_state.video = video
        else:
            video = st.session_state.video


    clip = get_clip()

    # Video preview in the sidebar
    frame_id = st.slider("Video Frame",min_value = 0,max_value = len(video.frames))
    st.image(video.frames[frame_id].img,use_column_width = True)

prompts_dict =  {
    "Base":[
        "background",
        "a black or colored screen with texts",
        "blank",
        "unknown",
        "a blurry picture",
    ],
    "Landscape":[
        'an urban area',
        'a building',
        'a nature landscape',
        'a city street',
        'a school',
        'inside a house',
    ],
    "Romantic":[
        'a woman is undressed, naked, or shown in a sexy way',
        'women breasts',
        'people kissing',
        'couple making love',
    ],
    "Action":[
        "people flying on brooms",
    ],
    "Dialogue":[
        'a young woman',
        'a young man',
        'an old woman',
        'an old man',
        'two women speaking together',
        'two men speaking together',
        'a man and a woman speaking together',
        'a group of persons',
        'a group of men',
        'a group of women',
    ]
}

clip.set_prompts(prompts_dict)

prompts_default = json.dumps(prompts_dict,sort_keys=True, indent=4)

with st.sidebar.form("prompts"):
    new_prompts_dict = json.loads(st.text_area("Prompts",prompts_default,height = 300))

    submitted = st.form_submit_button("Submit")
    if submitted:
        clip.set_prompts(new_prompts_dict)
        st.sidebar.write(f"{len(clip.prompts_list)} prompts uploaded in CLIP")
        with st.spinner('Bechdelizing the video ...'):
            preds,probas = clip.predict(video)

            st.session_state.preds = (preds,probas)

def make_fig_frame_probas(probas,i,clip,top = None,th = 0.2):
    probas_frame = probas.iloc[i].reset_index()
    probas_frame.columns = ["prompt","proba"]
    probas_frame = probas_frame.sort_values("proba",ascending = False).head(top)
    probas_frame = probas_frame.merge(clip.prompts,on = "prompt")
    probas_frame = probas_frame.query(f"proba > {th}")
    fig = px.bar(probas_frame,x = "prompt",y = "proba",color = "category",category_orders={'prompt': probas_frame["prompt"].tolist()})
    return fig

def make_fig_timeline(preds,clip):

    x = (preds.melt(ignore_index = False)
        .reset_index(drop = False)
        .rename(columns = {"index":"frame_id","variable":"prompt"})
    )

    x["rank"] = x.groupby(["frame_id"])["value"].transform("rank",ascending = False)

    x = x.query("rank<=1")

    x = x.merge(clip.prompts,on = "prompt").sort_values("frame_id")

    x["sequence_id"] = x.groupby("prompt")["frame_id"].transform(fn_timeline)

    timeline = convert_to_timeline(x,"prompt",show = False,xaxis_time=True)
    timeline = timeline.merge(clip.prompts,on = "prompt")

    fig = px.timeline(timeline,
        x_start = "start",
        x_end = "end",
        color = "prompt",
        y = "category",
        #     facet_row = "category",
        color_discrete_sequence = px.colors.qualitative.Alphabet
    )
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.5,
        xanchor="right",
        x=1
    ))
    return fig



if "preds" in st.session_state:
    preds,probas = st.session_state.preds


    with st.expander("Frame Analysis"):

        frame_id = st.slider("Video Frame",min_value = 0,max_value = len(video.frames),key = "slider2")

        col1,col2 = st.columns(2)

        # Video preview in the sidebar
        col1.image(video.frames[frame_id].img,use_column_width = True)

        # Split probas
        fig = make_fig_frame_probas(probas,frame_id,clip,top = 5,th = 0.1)
        col2.plotly_chart(fig,use_container_width = True)

    with st.expander("Full video timeline analysis"):

        fig = make_fig_timeline(preds,clip)
        st.plotly_chart(fig,use_container_width = True)




