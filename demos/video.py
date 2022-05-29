import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import os
import io
import time


import bechdelai
from bechdelai.vision.img import Img
from bechdelai.vision.faces import FacesDetector

st.set_page_config(page_title="BechdelAI", page_icon="🎥", layout="wide", initial_sidebar_state="auto", menu_items=None)

st.sidebar.image("demos/logo.png")
st.sidebar.write("## Video analysis")


