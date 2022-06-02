import streamlit as st
import pandas as pd
import plotly.express as px

DATA_URL = 'http://hollywoodagegap.com/movies.csv'


@st.cache
def load_data():
    return pd.read_csv(DATA_URL)


def define_the_oldest(df):
    gender_list = []
    for index, row in df.iterrows():
        if row["Actor 1 Age"] > row["Actor 2 Age"]:
            gender_list.append(row["Actor 1 Gender"])
        elif row["Actor 2 Age"] > row["Actor 1 Age"]:
            gender_list.append(row["Actor 2 Gender"])
        else:
            gender_list.append("same")
    return gender_list


def main():
    st.set_page_config(layout="wide")
    st.title('Hollywood Age Gap')
    raw_data = load_data()

    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(raw_data)

    st.subheader('Age Gap Visualization')
    data = raw_data.copy()
    data["Is_hetero"] = data["Actor 2 Gender"] != data["Actor 1 Gender"]
    data["Gender of the oldest"] = define_the_oldest(data)
    fig = px.histogram(data, x="Age Difference",
                       color="Gender of the oldest",
                       marginal="box",
                       hover_data=data.columns,
                       color_discrete_map={
                           "woman": "#f9ac23",
                           "man": "#2fd3D3",
                           "same": "#000000"
                       },
                       template="simple_white"
                       )
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
