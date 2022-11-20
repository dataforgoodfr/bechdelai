import streamlit as st

st.set_page_config(layout="wide",page_title="BechdelAI", page_icon="🎥")
st.write("# BechdelAI")
st.sidebar.image("static/logo.png")

st.info("""
Fighting sexism and gender discrimination in cinema and media with AI. The BechdelAI tool **helps automate the Bechdel test**, to measure women (under)representation in cinema and audiovisual media.
""")


st.write("""
## References
- Project page https://dataforgood.fr/projects/bechdelai
- Open source code https://github.com/dataforgoodfr/bechdelai

## Contact
Send an email to hellodataforgood@gmail.com
""")

