import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

st.title("Test CSV Upload with AgGrid")

# File uploader
uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

# Read CSV
df = pd.read_csv(uploaded_file)

# HARD sanitize for Arrow compatibility
df = df.reset_index(drop=True)
df.columns = [str(c) for c in df.columns]

# Convert all columns to Arrow-compatible types
for col in df.columns:
    # Replace pandas NA/NaN with None
    df[col] = df[col].where(pd.notna(df[col]), None)
    # Convert pandas Extension types or objects to native Python scalars
    df[col] = df[col].apply(lambda x: x.item() if hasattr(x, "item") else x)
    # Force remaining unknown types to str
    df[col] = df[col].apply(lambda x: x if isinstance(x, (str, int, float, type(None))) else str(x))

# Debug info
st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

# Render AgGrid safely
AgGrid(df, height=600)
