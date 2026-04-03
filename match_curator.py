import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

st.title("CSV Test with AgGrid")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

# Reset index and sanitize columns
df = df.reset_index(drop=True)
df.columns = [str(c) for c in df.columns]

# Force all columns to Python-native types for Arrow
for col in df.columns:
    if pd.api.types.is_integer_dtype(df[col]):
        df[col] = df[col].astype("Int64").astype(object)  # nullable integers -> object
    elif pd.api.types.is_float_dtype(df[col]):
        df[col] = df[col].astype(float)
    elif pd.api.types.is_bool_dtype(df[col]):
        df[col] = df[col].astype(object)
    else:
        # Anything else (StringDtype, object, categorical) -> str or None
        df[col] = df[col].where(pd.notna(df[col]), None).astype(object)

# Debug
st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

# Render table
AgGrid(df, height=600)
