import streamlit as st
import pandas as pd
import numpy as np

DATA_URL = ('http://hollywoodagegap.com/movies.csv')

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    return data


st.title('Hollywood Age Gap')
data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Écarts d\'âge')
hist_values = np.histogram(data['Age Difference'], bins=10)[0]
actor1_older = data[data['Actor 1 Age']>data['Actor 2 Age']]
actor2_older = data[data['Actor 1 Age']<data['Actor 2 Age']]
older_woman = pd.concat([actor1_older[actor1_older['Actor 1 Gender'] == 'woman'], actor2_older[actor2_older['Actor 2 Gender'] == 'woman']])
older_man = pd.concat([actor1_older[actor1_older['Actor 1 Gender'] == 'man'], actor2_older[actor2_older['Actor 2 Gender'] == 'man']])

st.write(older_woman.shape)
st.write(older_man.shape)

st.bar_chart(np.histogram(older_man['Age Difference'], bins=20)[0])
st.bar_chart(np.histogram(older_woman['Age Difference'], bins=20)[0])

#
# st.subheader('Number of pickups by hour')
# hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
# st.bar_chart(hist_values)
#
# # Some number in the range 0-23
# hour_to_filter = st.slider('hour', 0, 23, 17)
# filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
#
# st.subheader('Map of all pickups at %s:00' % hour_to_filter)
# st.map(filtered_data)