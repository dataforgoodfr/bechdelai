import os
import matplotlib.pyplot as plt
import streamlit as st

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import cv2
import tensorflow as tf
from utils import analyze

gpu_devices = tf.config.experimental.list_physical_devices("GPU")
if any(gpu_devices):
    tf.config.experimental.set_memory_growth(gpu_devices[0], True)
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from doctr.utils.visualization import visualize_page

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
    st.title("Poster analysis with docTR")
    cols = st.columns((1, 1))
    cols[0].subheader("Input page")
    st.sidebar.title("Document selection")
    st.set_option("deprecation.showfileUploaderEncoding", False)
    uploaded_file = st.sidebar.file_uploader(
        "Upload files", type=["pdf", "png", "jpeg", "jpg"]
    )

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".pdf"):
            doc = DocumentFile.from_pdf(uploaded_file.read()).as_images()
        else:
            doc = DocumentFile.from_images(uploaded_file.read())
        page_idx = 0
        cols[0].image(doc[page_idx])

    st.sidebar.write("\n")
    if st.sidebar.button("Analyze page"):
        if uploaded_file is None:
            st.sidebar.write("Please upload a document")
        else:
            with st.spinner("Loading model..."):
                predictor = load_ocr_model()
            with st.spinner("Analyzing..."):
                out = predictor([doc[page_idx]])
                page_export = out.pages[0].export()
                results = analyze(page_export)
                cols[1].subheader("Results")
                cols[1].table(results)
            with st.expander("For debug purpose"):
                st.write(page_export)


if __name__ == "__main__":
    main()
