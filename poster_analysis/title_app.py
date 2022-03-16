import os
from pathlib import Path

import streamlit as st

from movie_api import get_movie_poster, search_movie, download_movie_poster
from utils import identify_faces
import shutil

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf
import numpy as np
import cv2

from utils import extract_entities

gpu_devices = tf.config.experimental.list_physical_devices("GPU")
if any(gpu_devices):
    tf.config.experimental.set_memory_growth(gpu_devices[0], True)
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

DET_ARCHS = ["db_resnet50", "db_mobilenet_v3_large"]
RECO_ARCHS = ["crnn_vgg16_bn", "crnn_mobilenet_v3_small", "master", "sar_resnet31"]


@st.cache(allow_output_mutation=True)
def load_ocr_model():
    det_arch = "db_resnet50"
    reco_arch = "crnn_vgg16_bn"
    predictor = ocr_predictor(det_arch, reco_arch, pretrained=True)
    return predictor


def main():
    st.set_page_config(layout="wide")
    st.title("Movie analysis from posters")
    cols = st.columns((2, 1))
    title_input = st.text_input("Entrez un titre de film")

    if title_input:
        poster_path = "posters/000001.jpg"
        with st.spinner("fetching informations ..."):
            shutil.rmtree(poster_path, ignore_errors=True)
            download_movie_poster(title_input)
        if Path(poster_path).exists():
            movie_info = search_movie(title_input)
            cols[0].write(movie_info)
            doc = DocumentFile.from_images(poster_path)
            page_idx = 0
            cols[1].image(doc[page_idx])

            page_idx = 0
            st.sidebar.write("\n")
            if st.button("Analyze page"):
                with st.spinner("Loading model..."):
                    predictor = load_ocr_model()
                with st.spinner("Analyzing..."):
                    out = predictor([doc[page_idx]])
                    page_export = out.pages[0].export()
                    results = extract_entities(page_export)
                    results.apply(
                        lambda x: identify_faces(
                            x.Q_id, f"{title_input} {x.Name}", doc[page_idx]
                        ),
                        axis=1,
                    )
                    st.subheader("Results")
                    st.table(results)
                with st.expander("For debug purpose"):
                    st.write(page_export)


if __name__ == "__main__":
    main()
