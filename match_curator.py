import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

st.title("Test")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

# HARD sanitize
df = df.reset_index(drop=True)
df.columns = [str(c) for c in df.columns]

# Convert all columns to plain Python objects for PyArrow/AgGrid
df = df.astype(object).where(pd.notna(df), None)

st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

AgGrid(df, height=600)
