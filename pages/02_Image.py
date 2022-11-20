import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from PIL import Image
import os
import io
import time
import sys
sys.path.append("c:/git/bechdelai")

from bechdelai.image.face_detection import FacesDetector
from bechdelai.image.gender_detection import GenderDetector
from bechdelai.image.vilt import ViLT
from bechdelai.image.img import Img

st.set_page_config(layout="wide",page_title="BechdelAI - Image", page_icon="🎥")

st.write("# BechdelAI - Analyzing an image")
st.sidebar.image("static/logo.png")
st.info("This module can be used to analyze gender representation in a video")


uploaded_file = st.sidebar.file_uploader("Upload image", type=None, accept_multiple_files=False, key="upload")

if uploaded_file is not None:
    name = uploaded_file.name
    if "name" in st.session_state:
        if name != st.session_state.name:
            st.session_state.bechdelized = None
    st.session_state.name = name

    st.sidebar.write(uploaded_file.name)

    bytes_data = uploaded_file.getvalue()
    img = Img(Image.open(io.BytesIO(bytes_data))).resize(width = 600)
    container = st.sidebar.empty()
    container.image(img.array)

    # img = Img(path)
    fd = FacesDetector()
    gd = GenderDetector()

    if 'bechdelized' not in st.session_state or st.session_state.bechdelized is None:

        with st.spinner('Bechdelizing this image ...'):
            # my_bar = st.progress(0.0)

            rois,faces = fd.detect(img.array,method = "retinaface",padding = 20)
            probas = gd.predict(faces)
            results,metrics = gd.analyze_probas(probas)
            img_with_faces = fd.show_faces_on_image(img.array,rois,width = 3,genders = probas["gender"])
            # fd.show_all_faces(faces,titles = probas["gender"])
            # fd.show_faces_on_image(img.array,rois,)


            # faces,faces_data,rois,representation = detector.analyze_gender_representation(img.array,progress_streamlit = my_bar,padding = 10)
            # img_with_faces = detector.show_faces_on_image(img.array,rois,width = 3)

        st.session_state.bechdelized = {
            "faces":faces,
            "probas":probas,
            "rois":rois,
            "metrics":(results,metrics),
            "img_with_faces":img_with_faces,
        }

    else:
        faces = st.session_state.bechdelized["faces"]
        probas = st.session_state.bechdelized["probas"]
        rois = st.session_state.bechdelized["rois"]
        results,metrics = st.session_state.bechdelized["metrics"]
        img_with_faces = st.session_state.bechdelized["img_with_faces"]
    
    displayed_metrics = st.empty()
    m1,m2,m3,m4,m5,m6 = displayed_metrics.columns(6)

    woman_area = metrics["women_area"]
    man_area = metrics["men_area"]
    woman_delta = "+" if woman_area > man_area else "-"
    man_delta = "+" if woman_area < man_area else "-"

    m1.metric("Space occupied by women %",f"{round(woman_area * 100,2)}%",woman_delta)
    m2.metric("Space occupied by men %",f"{round(man_area * 100,2)}%",man_delta)
    m3.metric("Number of women",f"{int(metrics['n_women'])}",f"Among {metrics['n_characters']} characters",delta_color="off")
    m4.metric("Number of men",f"{int(metrics['n_men'])}",f"Among {metrics['n_characters']} characters",delta_color="off")
    m5.metric("Under-representation (by space)",metrics['ratio_area'])
    m6.metric("Under-representation (by count)",metrics['ratio_count'])

    #     metrics = {
    #         "women_area":woman_area,
    #         "men_area":man_area,
    #         "n_women":woman_count,
    #         "n_men":man_count,
    #         "n_characters":len(faces),
    #         "area_gap":woman_area/man_area,
    #         "count_gap":woman_count/man_count,
    #     }





    col1,col2 = st.columns([1,2])
    col1.image(np.array(img_with_faces))

    with col2.expander("Gender identification",expanded=True):

        st.write(results)
        st.write(probas)

    with col2.expander("Visual Question Answering"):
        

        query = st.text_input("Enter your query for the picture")

        submit = st.button("Ask your question")

        if submit:
            vilt = ViLT()
            preds_query,probas_query = vilt.predict([img.array],query)
            results_query = probas_query.iloc[0].sort_values(ascending = False).head(5).reset_index()
            st.bar_chart(results_query,x = "index",y = 0)



    # col1.metric("Women %",f"{round(woman_area * 100,2)}%",woman_delta)
    # col2.metric("Men %",f"{round(man_area * 100,2)}%",man_delta)
    # col3.metric("Number of characters",len(faces))
    # col4.metric("Under-representation",ratio)

    # with st.expander("Edit gender identification",expanded = True):

    #     # form = st.form("my_form")
    #     form_data = []

    #     for i in range(len(faces)):

    #         row = faces_data.iloc[i]


    #         with st.container():
    #             col1,col2,col3 = st.columns(3)
    #             col1.image(faces[i])
    #             option = col2.selectbox("Choose gender",["Woman","Man"],["Woman","Man"].index(row["gender"]),key = f"select{i}")
    #             col3.metric("% poster covered",f'{round(row["percentage"] * 100,2)}%')
    #             form_data.append({"face":i,"gender":option,"area":row["percentage"]})
    #             st.markdown("""---""")

    #     form_data = pd.DataFrame(form_data)
    #     agg = form_data.groupby("gender").agg({"area":"sum","face":"count"})
    #     representation = agg["area"]
    #     count = agg["face"]
    #     st.sidebar.write(representation)

    #     # submit = form.form_submit_button("Submit")
    #     # if submit:

    #     col1,col2,col3,col4,col5,col6 = metrics.columns(6)
    #     woman_area = representation.get('Woman',0.0)
    #     man_area = representation.get('Man',0.0)
    #     woman_count = count.get("Woman",0)
    #     man_count = count.get("Man",0)

    #     woman_delta = "+" if woman_area > man_area else "-"
    #     man_delta = "+" if woman_area < man_area else "-"

    #     if man_area == 0 and woman_area == 0:
    #         ratio = "0% 👩🧑"
    #     elif man_area == 0:
    #         ratio = "100% 👩"
    #     elif woman_area == 0:
    #         ratio = "100% 🧑"
    #     elif woman_area  > man_area:
    #         ratio = f"{round(woman_area/man_area,1)}x 👩"
    #     else:
    #         ratio = f"{round(man_area/woman_area,1)}x 🧑"

    #     if man_count == 0 and woman_count == 0:
    #         ratio_count = "0 👩🧑"
    #     if man_count == woman_count:
    #         ratio_count = "👩 = 🧑"
    #     elif man_count == 0:
    #         ratio_count = "100% 👩"
    #     elif woman_count == 0:
    #         ratio_count = "100% 🧑"
    #     elif woman_count  > man_count:
    #         ratio_count = f"{round(woman_count/man_count,1)}x 👩"
    #     else:
    #         ratio_count = f"{round(man_count/woman_count,1)}x 🧑"


    #     metrics = {
    #         "women_area":woman_area,
    #         "men_area":man_area,
    #         "n_women":woman_count,
    #         "n_men":man_count,
    #         "n_characters":len(faces),
    #         "area_gap":woman_area/man_area,
    #         "count_gap":woman_count/man_count,
    #     }

    #     metrics = pd.DataFrame(pd.Series(metrics),columns = [name]).T



    #     copy = st.button("Copy results")
    #     if copy:
    #         metrics.to_clipboard()