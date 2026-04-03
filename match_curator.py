import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

st.title("Test CSV with Arrow-safe conversion")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

# Force native Python types via object numpy arrays
df = pd.DataFrame(
    {col: df[col].to_numpy(dtype=object) for col in df.columns}
)

st.write("Shape:", df.shape)
st.write(df.head())
st.write(df.dtypes)

AgGrid(df, height=600)
