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

# Force all cells into Python-native types
def make_arrow_safe(df):
    for col in df.columns:
        # Replace pd.NA with None
        df[col] = df[col].where(pd.notna(df[col]), None)
        # Convert pandas Extension types to native Python types
        df[col] = df[col].apply(lambda x: x if x is None else x.item() if hasattr(x, 'item') else x)
        # Force everything to str/int/float/None if mixed
        df[col] = df[col].apply(lambda x: x if isinstance(x, (str, int, float, type(None))) else str(x))
    return df

df = make_arrow_safe(df)

st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

AgGrid(df, height=600)
