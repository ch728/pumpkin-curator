import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, JsCode

st.set_page_config(page_title="Pumpkin Match Curator", layout="wide")
st.title("Pumpkin Match Curation (Click-to-Select)")

# -----------------------------
# Upload CSV
# -----------------------------
uploaded_file = st.file_uploader("Upload match CSV for curation", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

# -----------------------------
# Initialize columns
# -----------------------------
if "Include" not in df.columns:
    df.insert(0, "Include", False)  # unchecked by default
if "Selected_Match" not in df.columns:
    df["Selected_Match"] = df["Match_1"]

# -----------------------------
# AgGrid JS for highlighting / click
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
# Configure AgGrid using original DataFrame
# -----------------------------
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, filter=True, sortable=True)

# Include column
gb.configure_column("Include", editable=True, type=["booleanColumn"], width=80)

# Source column (non-editable)
if "Source" in df.columns:
    gb.configure_column("Source", editable=False, cellStyle=source_cell_style, width=150)

# Match columns
for i in range(1, 6):
    col = f"Match_{i}"
    if col in df.columns:
        gb.configure_column(col, editable=True, cellStyle=cell_style_jscode, onCellClicked=click_js)

# Selected_Match column
gb.configure_column("Selected_Match", editable=False, width=200)

# Enable copy/paste
gb.configure_grid_options(enableRangeSelection=True, enableCopy=True)
grid_options = gb.build()

# -----------------------------
# Convert DataFrame to native Python types to avoid Arrow issues
# -----------------------------
rows = df.astype(object).where(pd.notna(df), None).to_dict(orient="records")

# Convert nullable boolean columns to native bool
for r in rows:
    for k, v in r.items():
        if isinstance(v, pd._libs.missing.NAType):
            r[k] = None
        elif isinstance(v, (pd.BooleanDtype, pd._libs.missing.NAType)):
            # fallback: ensure bool
            r[k] = bool(v) if v is not None else None

# -----------------------------
# Render AgGrid
# -----------------------------
grid_response = AgGrid(
    rows,
    gridOptions=grid_options,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    update_on=["cellValueChanged", "cellEditingStopped"],
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
    height=600
)

# Convert back to DataFrame for downstream operations
df = pd.DataFrame(grid_response["data"])

# -----------------------------
# Download / Export
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
