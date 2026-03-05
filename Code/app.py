import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import branca.colormap as cm
from pathlib import Path
import requests

# =========================
# CONFIG: PUT YOUR FILE URL
# =========================
# This must be a *direct download* URL to the .gpkg (not a preview page).
# Examples that usually work:
# - Box "shared/static/....gpkg"
# - S3 https://.../file.gpkg
GPKG_URL = "https://uchicago.box.com/s/5mirakc5f539szi8kqwckt4tt493vm6y"

# If you prefer not to hardcode the URL, you can set it as a Streamlit secret:
# st.secrets["GPKG_URL"]
# and then do: GPKG_URL = st.secrets["GPKG_URL"]

# --- Paths (anchor to this file, not working directory) ---
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = (APP_DIR / "../Data/Derived_Data").resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

GPKG_PATH = (DATA_DIR / "gdf_merged.gpkg").resolve()

# --- Streamlit page setup ---
st.set_page_config(page_title="Interactive Hazard Map", layout="wide")
st.title("Interactive Environmental Hazard Map")

# -------------------------
# DEBUG BLOCK (pre-download)
# -------------------------
st.subheader("Debug: File checks (pre-download)")
st.write("APP_DIR:", str(APP_DIR))
st.write("DATA_DIR:", str(DATA_DIR))
st.write("GPKG_PATH:", str(GPKG_PATH))
st.write("Exists:", GPKG_PATH.exists())
if DATA_DIR.exists():
    try:
        st.write("DATA_DIR listing:", sorted(os.listdir(DATA_DIR))[:200])
    except Exception as e:
        st.write("Could not list DATA_DIR:", repr(e))

if GPKG_PATH.exists():
    try:
        st.write("Size (bytes):", GPKG_PATH.stat().st_size)
        head = GPKG_PATH.read_bytes()[:200]
        st.write("First 200 bytes (utf-8, replace errors):", head.decode("utf-8", errors="replace"))
    except Exception as e:
        st.write("Could not read file header:", repr(e))

# -------------------------
# OPTION 1 FIX: Download .gpkg at runtime
# -------------------------
@st.cache_data(show_spinner=True)
def ensure_gpkg(local_path_str: str, url: str) -> str:
    """
    Ensures the GeoPackage exists locally and looks non-trivial in size.
    Downloads it if missing or obviously invalid (e.g., 1 byte / LFS pointer / empty).
    Returns the local path as a string.
    """
    local_path = Path(local_path_str)

    if not url or "PASTE_DIRECT_DOWNLOAD_URL" in url:
        raise ValueError(
            "GPKG_URL is not set. Replace GPKG_URL with a direct-download URL to gdf_merged.gpkg "
            "or store it in st.secrets['GPKG_URL']."
        )

    # Heuristic: anything under ~50KB is almost certainly not a real tract-level gpkg
    needs_download = (not local_path.exists()) or (local_path.stat().st_size < 50_000)

    if needs_download:
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Stream download to avoid memory spikes
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            tmp_path = local_path.with_suffix(".tmp")
            with open(tmp_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

        # Atomic-ish replace
        tmp_path.replace(local_path)

    return str(local_path)

with st.spinner("Ensuring GeoPackage is available..."):
    gpkg_local_path = ensure_gpkg(str(GPKG_PATH), GPKG_URL)

# --------------------------
# DEBUG BLOCK (post-download)
# --------------------------
st.subheader("Debug: File checks (post-download)")
st.write("GPKG_PATH:", gpkg_local_path)
try:
    st.write("Exists:", Path(gpkg_local_path).exists())
    st.write("Size (bytes):", Path(gpkg_local_path).stat().st_size)
    head = Path(gpkg_local_path).read_bytes()[:200]
    st.write("First 200 bytes (utf-8, replace errors):", head.decode("utf-8", errors="replace"))
except Exception as e:
    st.write("Post-download file check error:", repr(e))

# Optional: Fiona driver support check (helps diagnose GPKG driver issues)
try:
    import fiona  # noqa: F401
    import fiona
    st.write(
        "Fiona supported drivers (subset):",
        {k: v for k, v in fiona.supported_drivers.items() if k in ["GPKG", "GeoJSON", "ESRI Shapefile"]},
    )
except Exception as e:
    st.write("Could not import fiona or read supported drivers:", repr(e))

# -------------------------
# Load GeoDataFrame
# -------------------------
@st.cache_data(show_spinner=True)
def load_gdf(gpkg_path_str: str):
    # Use Fiona engine if available (most compatible on hosted environments)
    try:
        return gpd.read_file(gpkg_path_str, layer="merged_layer", engine="fiona")
    except TypeError:
        # Older GeoPandas versions may not support engine= kwarg
        return gpd.read_file(gpkg_path_str, layer="merged_layer")

gdf_merged = load_gdf(gpkg_local_path)

# --- County filter dropdown ---
county_options = [None] + sorted(gdf_merged["county_name"].dropna().unique())
selected_county = st.selectbox(
    "Filter map by county:",
    county_options,
    format_func=lambda x: "All Counties" if x is None else x,
)

# Apply filter only if a county is selected
if selected_county:
    gdf_filtered = gdf_merged[gdf_merged["county_name"] == selected_county]
else:
    gdf_filtered = gdf_merged

# --- User selects numeric column ---
numeric_columns = gdf_merged.select_dtypes(include=["number"]).columns.tolist()
selected_column = st.selectbox(
    "Select a column to visualize:",
    numeric_columns,
    index=numeric_columns.index("haz_idx") if "haz_idx" in numeric_columns else 0,
)

# --- Colormap definitions ---
colormap_options = {
    "Reds": cm.LinearColormap(["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"]),
    "Blues": cm.LinearColormap(["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"]),
    "Greens": cm.LinearColormap(["#edf8e9", "#bae4b3", "#74c476", "#31a354", "#006d2c"]),
    "YlOrRd": cm.LinearColormap(["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"]),
    "Viridis": cm.LinearColormap(
        ["#440154", "#482777", "#3e4989", "#31688e", "#26828e", "#1f9e89", "#35b779", "#6ece58", "#b5de2b", "#fde725"]
    ),
    "Plasma": cm.LinearColormap(
        ["#0d0887", "#3d049a", "#6300a7", "#8400b0", "#a11fb9", "#bd4fc1", "#d66bb9", "#ed91b3", "#fbcca0", "#f0f921"]
    ),
}

cmap_option = st.selectbox("Select a colormap:", list(colormap_options.keys()), index=0)

col_min = float(gdf_filtered[selected_column].min())
col_max = float(gdf_filtered[selected_column].max())
colormap = colormap_options[cmap_option].scale(col_min, col_max)
colormap.caption = selected_column

# --- Create Folium map centered on data ---
# Note: centroid on geographic CRS can warn; this is OK for centering.
center = [gdf_filtered.geometry.centroid.y.mean(), gdf_filtered.geometry.centroid.x.mean()]
m = folium.Map(location=center, zoom_start=6, tiles="CartoDB positron")

# --- Style function with safe fallback for missing values ---
def style_function(feature):
    val = feature["properties"].get(selected_column)
    if val is None:
        return {"fillColor": "#cccccc", "color": "#b0b0b0", "weight": 0.6, "fillOpacity": 0.7}
    return {"fillColor": colormap(val), "color": "#b0b0b0", "weight": 0.6, "fillOpacity": 0.7}

# --- Add GeoJSON layer with hover tooltip ---
folium.GeoJson(
    gdf_filtered.to_json(),
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["geoid_id", selected_column],
        aliases=["geoid_id:", f"{selected_column}:"],
        localize=True,
    ),
).add_to(m)

# --- Add colormap legend ---
colormap.add_to(m)

# --- Display map in Streamlit ---
st_folium(m, width=800, height=600)
