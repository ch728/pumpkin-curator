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

# Reset index and sanitize column names
df = df.reset_index(drop=True)
df.columns = [str(c) for c in df.columns]

# Convert all columns to Python-native types for Arrow
for col in df.columns:
    # Replace all missing values with None
    df[col] = df[col].where(pd.notna(df[col]), None)
    
    # Convert pandas extension types to native Python scalars
    if pd.api.types.is_integer_dtype(df[col]):
        df[col] = df[col].astype("Int64").astype(object)
    elif pd.api.types.is_float_dtype(df[col]):
        df[col] = df[col].astype(float)
    else:
        # Everything else (strings, objects) -> str or None
        df[col] = df[col].apply(lambda x: str(x) if x is not None else None)

# Debug: print shape and head
st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

# Render AgGrid
AgGrid(df, height=600)
