import os
import streamlit as st
import pydeck as pdk
import geopandas as gpd
from os.path import join
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="IL Data Centers", layout="wide")

# Optional: Mapbox token (recommended for mapbox styles like light-v10)
# Prefer Streamlit secrets: .streamlit/secrets.toml -> MAPBOX_API_KEY="..."
mapbox_token = st.secrets.get("MAPBOX_API_KEY", None) or os.getenv("MAPBOX_API_KEY", None)
if mapbox_token:
    pdk.settings.mapbox_api_key = mapbox_token
else:
    st.info(
        "No MAPBOX_API_KEY found. Map tiles may not render with mapbox:// styles. "
        "Add MAPBOX_API_KEY to .streamlit/secrets.toml or your environment."
    )

PROJECT_ROOT = Path.cwd()

if not (PROJECT_ROOT / "Data").exists():
    PROJECT_ROOT = PROJECT_ROOT.parent

DER_DATA_DIR = PROJECT_ROOT / "Data" / "Derived_Data"
TRACT_DIR = PROJECT_ROOT / "Data" / "Derived_Data" / "tl_2025_17_tract"
RAW_DATA_DIR = PROJECT_ROOT / "Data" /"Raw_Data/data_center_geodata/im3_open_source_data_center_atlas"

data_centers = pd.read_csv(RAW_DATA_DIR / 'im3_open_source_data_center_atlas.csv')
tracts_path = TRACT_DIR / "tl_2025_17_tract.shp"
tracts = gpd.read_file(tracts_path).to_crs("EPSG:4326")

data_centers = data_centers.dropna(subset=['lon', 'lat']).copy()
geometry = gpd.points_from_xy(data_centers['lon'], data_centers['lat'])
data_centers_gdf = gpd.GeoDataFrame(data_centers, geometry=geometry, crs="EPSG:4326")
data_centers_il = data_centers_gdf[data_centers_gdf['state'] == 'Illinois']



# --- PyDeck layers ---
tracts_geojson = tracts.__geo_interface__
tracts_layer = pdk.Layer(
    "GeoJsonLayer",
    data=tracts_geojson,
    stroked=True,
    filled=True,
    extruded=False,
    get_fill_color=[232, 232, 232, 160],
    get_line_color=[176, 176, 176, 180],
    line_width_min_pixels=1,
    pickable=False,
)

points_layer = pdk.Layer(
    "ScatterplotLayer",
    data=data_centers_il,
    get_position=["lon", "lat"],
    get_radius=250,
    radius_min_pixels=4,
    radius_max_pixels=18,
    get_fill_color=[220, 20, 60, 200],
    get_line_color=[0, 0, 0, 200],
    line_width_min_pixels=1,
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=40.0,
    longitude=-89.0,
    zoom=6.2,
    pitch=0,
)

tooltip = {
    "html": """
    <b>Data center</b><br/>
    {name}<br/>
    <b>City:</b> {city}<br/>
    <b>State:</b> {state}<br/>
    <b>Coords:</b> {lat}, {lon}
    """,
    "style": {"backgroundColor": "white", "color": "black"},
}

deck = pdk.Deck(
    layers=[tracts_layer, points_layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/light-v10",
    tooltip=tooltip,
)

st.title("Illinois Data Centers (PyDeck)")
st.pydeck_chart(deck, use_container_width=True) 
