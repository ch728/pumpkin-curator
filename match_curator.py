import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

st.title("CSV Viewer with Pandas")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

# Read CSV with pandas
df = pd.read_csv(uploaded_file)

# HARD sanitize: convert all columns to native Python types
for col in df.columns:
    df[col] = df[col].astype(object)  # ensures no StringDtype / Arrow issues
    df[col] = df[col].where(pd.notna(df[col]), None)

st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

AgGrid(df, height=600)
