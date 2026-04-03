import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

st.title("Test")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

df = df.fillna("")
for col in df.columns:
    df[col] = df[col].astype(str)

AgGrid(df, height=600)
