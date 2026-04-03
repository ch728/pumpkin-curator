import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode, JsCode


st.set_page_config(page_title="Pumpkin Match Curator", layout="wide")
st.title("Pumpkin Match Curation (Click-to-Select)")

# -----------------------------
# Upload match CSV
# -----------------------------
uploaded_file = st.file_uploader("Upload match CSV for curation", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

# Force Arrow-compatible dtypes immediately on load
df = df.convert_dtypes()  # promotes to nullable types
# Then immediately downcast to numpy-native types Arrow handles well
df = df.infer_objects()
# -----------------------------
# Initialize columns
# -----------------------------
if "Include" not in df.columns:
    df.insert(0, "Include", False)
df["Include"] = df["Include"].astype(bool)  # force native bool, never object
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
# Configure AgGrid
# -----------------------------
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, filter=True, sortable=True)

# Include column
gb.configure_column(
    "Include",
    editable=True,
    type=["booleanColumn"],
    cellRenderer=JsCode("""
        function(params) {
            return params.value ? '✅' : '☐';
        }
    """),
    cellEditor="agLargeTextCellEditor",
    width=80
)
# Source column (non-editable, gray)
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

# Enable copy/paste of all cells
gb.configure_grid_options(enableRangeSelection=True, enableCopy=True)

grid_options = gb.build()

# -----------------------------
# Render AgGrid
# -----------------------------
df.columns = [str(c) for c in df.columns]

# Convert all nullable pandas types to Arrow-compatible native types
for col in df.columns:
    col_dtype = df[col].dtype

    if pd.api.types.is_bool_dtype(col_dtype):
        df[col] = df[col].fillna(False).astype(bool)
    elif pd.api.types.is_integer_dtype(col_dtype):
        df[col] = df[col].fillna(0).astype("int64")
    elif pd.api.types.is_float_dtype(col_dtype):
        df[col] = df[col].astype("float64")
    else:
        df[col] = df[col].fillna("").astype(str)

grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
    height=600
)
df = pd.DataFrame(grid_response["data"])

# -----------------------------
# Save progress and export patch (downloads)
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

# Export patch CSV (exclude Source)
patch_df = df[df["Include"] == True][["Query", "Selected_Match"]].copy()
patch_df.columns = ["Old", "New"]
csv_patch = patch_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Patch CSV",
    data=csv_patch,
    file_name="patch.csv",
    mime="text/csv"
)
