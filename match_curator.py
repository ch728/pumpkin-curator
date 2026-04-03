import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

st.title("CSV Test with AgGrid")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

# Reset index and sanitize column names
df = df.reset_index(drop=True)
df.columns = [str(c) for c in df.columns]

# Convert all columns to Arrow-compatible Python types
for col in df.columns:
    # Replace missing values with None
    df[col] = df[col].where(pd.notna(df[col]), None)
    
    # Force dtype to object for strings / mixed types
    if pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
        df[col] = df[col].astype(object)
    
    # Nullable integers -> object
    elif pd.api.types.is_integer_dtype(df[col]):
        df[col] = df[col].astype(object)
    
    # Floats -> keep as float
    elif pd.api.types.is_float_dtype(df[col]):
        df[col] = df[col].astype(float)
    
    # Booleans -> object
    elif pd.api.types.is_bool_dtype(df[col]):
        df[col] = df[col].astype(object)
    
    # Other / unknown types -> str
    else:
        df[col] = df[col].astype(str)

# Debug output
st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

# Render AgGrid
AgGrid(df, height=600)
