import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, JsCode

st.title("Pumpkin Match Curator")

uploaded_file = st.file_uploader("Upload match CSV", type="csv")
if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)

# Initialize columns
if "Include" not in df.columns:
    df.insert(0, "Include", False)
if "Selected_Match" not in df.columns:
    df["Selected_Match"] = df["Match_1"]

# -----------------------------
# Convert all nullable types to native Python types
# -----------------------------
for col in df.columns:
    # Convert nullable booleans to native bool
    if pd.api.types.is_bool_dtype(df[col]):
        df[col] = df[col].astype(bool)
    # Convert nullable integers/floats to native int/float
    elif pd.api.types.is_integer_dtype(df[col]):
        df[col] = df[col].astype('Int64').astype(object)
    elif pd.api.types.is_float_dtype(df[col]):
        df[col] = df[col].astype(float)
    # Convert strings
    elif pd.api.types.is_string_dtype(df[col]):
        df[col] = df[col].astype(str)
    # Replace NaN/NA with None
    df[col] = df[col].where(pd.notna(df[col]), None)

# -----------------------------
# AgGrid setup
# -----------------------------
cell_style_jscode = JsCode("""
function(params) {
    if(params.data && params.value === params.data.Selected_Match) {
        return { 'backgroundColor': '#90EE90', 'textAlign': 'center', 'cursor': 'pointer', 'fontWeight': 'bold' };
    } else { return { 'textAlign': 'center', 'cursor': 'pointer' }; }
}
""")

click_js = JsCode("""
function(params) {
    params.node.setDataValue('Selected_Match', params.value);
    params.api.refreshCells({ rowNodes: [params.node], force: true });
}
""")

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, filter=True, sortable=True)
gb.configure_column("Include", editable=True, type=["booleanColumn"], width=80)

# Match columns
for i in range(1, 6):
    col = f"Match_{i}"
    if col in df.columns:
        gb.configure_column(col, editable=True, cellStyle=cell_style_jscode, onCellClicked=click_js)

gb.configure_column("Selected_Match", editable=False, width=200)
grid_options = gb.build()

# Render AgGrid
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    update_on=["cellValueChanged", "cellEditingStopped"],
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    height=600
)

# Updated DataFrame
df = pd.DataFrame(grid_response["data"])
st.write(df.head())
