import streamlit as st

import sys
sys.path.append("c:/git/bechdelai")

from bechdelai.image.face_detection import FacesDetector
from bechdelai.image.gender_detection import GenderDetector

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
    detector = FacesDetector()

    if 'bechdelized' not in st.session_state or st.session_state.bechdelized is None:

        with st.spinner('Bechdelizing this image ...'):
            my_bar = st.progress(0.0)
            faces,faces_data,rois,representation = detector.analyze_gender_representation(img.array,progress_streamlit = my_bar,padding = 10)
            img_with_faces = detector.show_faces_on_image(img.array,rois,width = 3)



        st.session_state.bechdelized = {
            "faces":faces,
            "faces_data":faces_data,
            "rois":rois,
            "representation":representation,
            "img_with_faces":img_with_faces,
        }

    else:
        faces = st.session_state.bechdelized["faces"]
        faces_data = st.session_state.bechdelized["faces_data"]
        rois = st.session_state.bechdelized["rois"]
        representation = st.session_state.bechdelized["representation"]
        img_with_faces = st.session_state.bechdelized["img_with_faces"]
    

    container.empty()
    container.image(np.array(img_with_faces))

    metrics = st.empty()
    # col1,col2,col3,col4 = metrics.columns(4)
    # woman_area = representation.get('Woman',0.0)
    # man_area = representation.get('Man',0.0)
    # woman_delta = "+" if woman_area > man_area else "-"
    # man_delta = "+" if woman_area < man_area else "-"

    # if man_area == 0 and woman_area == 0:
    #     title = "There are no characters in this picture"
    #     ratio = "0% 👩🧑"
    # elif man_area == 0:
    #     title = "There are only women 👩 in this picture"
    #     ratio = "100% 👩"
    # elif woman_area == 0:
    #     title = "There are only men 🧑 in this picture"
    #     ratio = "100% 🧑"
    # elif woman_area  > man_area:
    #     title = f"Women 👩 occupy **{round(woman_area/man_area,1)}** times more space than men 🧑 in this picture"
    #     ratio = f"{round(woman_area/man_area,1)} x 👩"
    # else:
    #     title = f"Men 🧑 occupy **{round(man_area/woman_area,1)}** times more space than women 👩 in this picture"
    #     ratio = f"{round(man_area/woman_area,1)} x 🧑" 

    

    # col1.metric("Women %",f"{round(woman_area * 100,2)}%",woman_delta)
    # col2.metric("Men %",f"{round(man_area * 100,2)}%",man_delta)
    # col3.metric("Number of characters",len(faces))
    # col4.metric("Under-representation",ratio)

    with st.expander("Edit gender identification",expanded = True):

        # form = st.form("my_form")
        form_data = []

        for i in range(len(faces)):

            row = faces_data.iloc[i]


            with st.container():
                col1,col2,col3 = st.columns(3)
                col1.image(faces[i])
                option = col2.selectbox("Choose gender",["Woman","Man"],["Woman","Man"].index(row["gender"]),key = f"select{i}")
                col3.metric("% poster covered",f'{round(row["percentage"] * 100,2)}%')
                form_data.append({"face":i,"gender":option,"area":row["percentage"]})
                st.markdown("""---""")

        form_data = pd.DataFrame(form_data)
        agg = form_data.groupby("gender").agg({"area":"sum","face":"count"})
        representation = agg["area"]
        count = agg["face"]
        st.sidebar.write(representation)

        # submit = form.form_submit_button("Submit")
        # if submit:

        col1,col2,col3,col4,col5,col6 = metrics.columns(6)
        woman_area = representation.get('Woman',0.0)
        man_area = representation.get('Man',0.0)
        woman_count = count.get("Woman",0)
        man_count = count.get("Man",0)

        woman_delta = "+" if woman_area > man_area else "-"
        man_delta = "+" if woman_area < man_area else "-"

        if man_area == 0 and woman_area == 0:
            ratio = "0% 👩🧑"
        elif man_area == 0:
            ratio = "100% 👩"
        elif woman_area == 0:
            ratio = "100% 🧑"
        elif woman_area  > man_area:
            ratio = f"{round(woman_area/man_area,1)}x 👩"
        else:
            ratio = f"{round(man_area/woman_area,1)}x 🧑"

        if man_count == 0 and woman_count == 0:
            ratio_count = "0 👩🧑"
        if man_count == woman_count:
            ratio_count = "👩 = 🧑"
        elif man_count == 0:
            ratio_count = "100% 👩"
        elif woman_count == 0:
            ratio_count = "100% 🧑"
        elif woman_count  > man_count:
            ratio_count = f"{round(woman_count/man_count,1)}x 👩"
        else:
            ratio_count = f"{round(man_count/woman_count,1)}x 🧑"


        metrics = {
            "women_area":woman_area,
            "men_area":man_area,
            "n_women":woman_count,
            "n_men":man_count,
            "n_characters":len(faces),
            "area_gap":woman_area/man_area,
            "count_gap":woman_count/man_count,
        }

        metrics = pd.DataFrame(pd.Series(metrics),columns = [name]).T

        col1.metric("Women %",f"{round(woman_area * 100,2)}%",woman_delta)
        col2.metric("Men %",f"{round(man_area * 100,2)}%",man_delta)
        col3.metric("Number of women",f"{int(woman_count)}",f"Among {len(faces)} characters",delta_color="off")
        col4.metric("Number of men",f"{int(man_count)}",f"Among {len(faces)} characters",delta_color="off")
        col5.metric("Under-representation (by area)",ratio)
        col6.metric("Under-representation (by count)",ratio_count)

        copy = st.button("Copy results")
        if copy:
            metrics.to_clipboard()