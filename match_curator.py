import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

st.title("Test")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

# HARD sanitize for Arrow compatibility
df = df.reset_index(drop=True)
df.columns = [str(c) for c in df.columns]

# Convert all columns to Arrow-compatible types
for col in df.columns:
    # Replace pd.NA or np.nan with None
    df[col] = df[col].where(pd.notna(df[col]), None)
    # Convert any pandas Extension types to native Python scalars
    df[col] = df[col].apply(lambda x: x.item() if hasattr(x, 'item') else x)
    # Finally, ensure type is one of str/int/float/None
    df[col] = df[col].apply(lambda x: x if isinstance(x, (str, int, float, type(None))) else str(x))

st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

# Render AgGrid safely
AgGrid(df, height=600)
