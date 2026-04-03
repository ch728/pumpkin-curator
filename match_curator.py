import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, JsCode

st.set_page_config(page_title="Pumpkin Match Curator", layout="wide")
st.title("Pumpkin Match Curation (Click-to-Select)")

# -----------------------------
# Upload match CSV
# -----------------------------
uploaded_file = st.file_uploader("Upload match CSV for curation", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

# -----------------------------
# FIX: Sanitize dataframe for AgGrid (critical for Streamlit Cloud)
# -----------------------------
df = df.reset_index(drop=True)
df.columns = [str(c) for c in df.columns]

df = df.fillna("")
for col in df.columns:
    df[col] = df[col].astype(str)

# -----------------------------
# Initialize columns
# -----------------------------
if "Include" not in df.columns:
    df.insert(0, "Include", False)

if "Selected_Match" not in df.columns:
    df["Selected_Match"] = df["Match_1"]

# Fix Include column back to boolean
df["Include"] = df["Include"].astype(str).map({"True": True, "False": False}).fillna(False)

# -----------------------------
# AgGrid JavaScript
# -----------------------------
cell_style_jscode = JsCode("""
function(params) {
    if(params.data && params.value === params.data.Selected_Match) {
        return {
            'backgroundColor': '#90EE90',
            'textAlign': 'center',
            'cursor': 'pointer',
            'fontWeight': 'bold'
        };
    } else {
        return {
            'textAlign': 'center',
            'cursor': 'pointer'
        };
    }
}
""")

source_cell_style = JsCode("""
function(params) {
    return {
        'backgroundColor': '#D3D3D3',
        'textAlign': 'center',
        'fontStyle': 'italic'
    };
}
""")

# SAFE click handler (removed refreshCells which breaks cloud)
click_js = JsCode("""
function(params) {
    if (!params || !params.node) return;
    params.node.setDataValue('Selected_Match', params.value);
}
""")

# -----------------------------
# Configure AgGrid
# -----------------------------
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, filter=True, sortable=True)

# Include column
gb.configure_column("Include", editable=True, type=["booleanColumn"], width=80)

# Source column
if "Source" in df.columns:
    gb.configure_column("Source", editable=False, cellStyle=source_cell_style, width=150)

# Match columns
for i in range(1, 6):
    col = f"Match_{i}"
    if col in df.columns:
        gb.configure_column(
            col,
            editable=True,
            cellStyle=cell_style_jscode,
            onCellClicked=click_js
        )

# Selected_Match column
gb.configure_column("Selected_Match", editable=False, width=200)

# Enable copy
gb.configure_grid_options(enableRangeSelection=True, enableCopy=True)

grid_options = gb.build()

# -----------------------------
# Render AgGrid
# -----------------------------
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
    height=600
)

df = pd.DataFrame(grid_response["data"])

# -----------------------------
# Export section
# -----------------------------
st.subheader("Download / Export")

# Save progress
csv_progress = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Progress CSV",
    data=csv_progress,
    file_name="curation_progress.csv",
    mime="text/csv"
)

# Export patch
patch_df = df[df["Include"] == True][["Query", "Selected_Match"]].copy()
patch_df.columns = ["Old", "New"]

csv_patch = patch_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Patch CSV",
    data=csv_patch,
    file_name="patch.csv",
    mime="text/csv"
)
