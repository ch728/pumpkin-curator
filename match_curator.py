import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

st.title("CSV Test with AgGrid")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

# Read CSV
df = pd.read_csv(uploaded_file)

# HARD sanitize for Arrow compatibility
df = df.reset_index(drop=True)
df.columns = [str(c) for c in df.columns]

# Replace all NaN / pd.NA with None
df = df.where(pd.notna(df), None)

# Convert all columns to Arrow-compatible Python scalars
for col in df.columns:
    df[col] = df[col].apply(lambda x: x if isinstance(x, (str, int, float, type(None))) else str(x))

# Show info for debugging
st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

# Render AgGrid
AgGrid(df, height=600)
