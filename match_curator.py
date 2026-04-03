import streamlit as st
import csv
from st_aggrid import AgGrid

st.title("CSV Viewer Without Pandas")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

# Read CSV into list of dictionaries (rows)
decoded = uploaded_file.read().decode("utf-8").splitlines()
reader = csv.DictReader(decoded)
data = [row for row in reader]

# Show row count and first few rows
st.write("Rows:", len(data))
st.write("First 3 rows:", data[:3])

# Render AgGrid
AgGrid(data, height=600)
