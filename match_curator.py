import streamlit as st
from st_aggrid import AgGrid

st.title("Test CSV without pandas")

uploaded_file = st.file_uploader("Upload CSV", type="csv")
if uploaded_file is None:
    st.stop()

# Read CSV using Python's built-in csv module
import csv
rows = []
with open(uploaded_file.name, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        rows.append(row)

st.write("Rows:", len(rows))
if rows:
    # Render AgGrid with list of dicts
    AgGrid(rows, height=600)
