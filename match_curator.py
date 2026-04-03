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

# Use Pandas 2.0 PyArrow backend
df = pd.read_csv(uploaded_file, dtype_backend="pyarrow")

# -----------------------------
# Initialize columns
# -----------------------------
if "Include" not in df.columns:
    df.insert(0, "Include", False)  # unchecked by default
if "Selected_Match" not in df.columns:
    df["Selected_Match"] = df["Match_1"]

# -----------------------------
# AgGrid JavaScript for highlighting
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
        'backgroundColor': '#D3D3D3',  // light gray
        'textAlign': 'center',
        'fontStyle': 'italic'
    };
}
""")

click_js = JsCode("""
function(params) {
    params.node.setDataValue('Selected_Match', params.value);
    params.api.refreshCells({
        rowNodes: [params.node],
        force: true
    });
}
""")

# -----------------------------
# Convert to Python-native types for AgGrid
# -----------------------------
df = df.to_pandas()  # Arrow -> native Python scalars
for col in df.columns:
    # Replace any missing values with None
    df[col] = df[col].where(pd.notna(df[col]), None)
    # Convert nullable booleans to bool
    if pd.api.types.is_bool_dtype(df[col]):
        df[col] = df[col].astype(bool)
    # Convert strings to native str
    elif pd.api.types.is_string_dtype(df[col]):
        df[col] = df[col].astype(str)

# -----------------------------
# Configure AgGrid
# -----------------------------
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, filter=True, sortable=True)

gb.configure_column("Include", editable=True, type=["booleanColumn"], width=80)

if "Source" in df.columns:
    gb.configure_column("Source", editable=False, cellStyle=source_cell_style, width=150)

for i in range(1, 6):
    col = f"Match_{i}"
    if col in df.columns:
        gb.configure_column(
            col,
            editable=True,
            cellStyle=cell_style_jscode,
            onCellClicked=click_js
        )

gb.configure_column("Selected_Match", editable=False, width=200)
gb.configure_grid_options(enableRangeSelection=True, enableCopy=True)
grid_options = gb.build()

# -----------------------------
# Render AgGrid
# -----------------------------
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    update_on=["cellValueChanged", "cellEditingStopped"],
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
    height=600
)

df = pd.DataFrame(grid_response["data"])

# -----------------------------
# Save progress and export patch
# -----------------------------
st.subheader("Download / Export")

csv_progress = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Progress CSV",
    data=csv_progress,
    file_name="curation_progress.csv",
    mime="text/csv"
)

patch_df = df[df["Include"] == True][["Query", "Selected_Match"]].copy()
patch_df.columns = ["Old", "New"]
csv_patch = patch_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Patch CSV",
    data=csv_patch,
    file_name="patch.csv",
    mime="text/csv"
)
