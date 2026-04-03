import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

st.title("Test CSV Upload with AgGrid")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

# HARD sanitize for Arrow compatibility
df = df.reset_index(drop=True)
df.columns = [str(c) for c in df.columns]

# Convert all columns to Arrow-compatible native Python types
for col in df.columns:
    # Replace pd.NA / NaN with None
    df[col] = df[col].where(pd.notna(df[col]), None)
    
    # Convert pandas Extension types to native Python scalars
    if pd.api.types.is_integer_dtype(df[col]) or pd.api.types.is_float_dtype(df[col]):
        df[col] = df[col].astype(float)  # float handles both int and float safely
    else:
        df[col] = df[col].astype(str)  # force everything else to plain string
        df[col] = df[col].replace("nan", None)  # restore None for missing values

# Debug info
st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

# Render AgGrid
AgGrid(df, height=600)
