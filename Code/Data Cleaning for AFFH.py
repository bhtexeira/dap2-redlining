import geopandas as gpd
import os
import altair as alt
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from pathlib import Path

try:
    script_dir = Path(__file__).parent
except NameError:
    script_dir = Path.cwd()  # for notebooks / Quarto

url = "https://uchicago.box.com/shared/static/hu6l6g8rdhkxjlly80gq8tgp37fqpgek.csv"
df_affh = pd.read_csv(url, encoding='latin-1')

df_il_cleaned = df_affh.copy()
df_il_cleaned = df_il_cleaned[df_il_cleaned["geoid"].between(17000000000, 17999999999, inclusive="both")]

# reduce number of columns to less than 300
req_cols = ["geoid", "Total_Population2020", "white_2020", "black_2020", "native_2020", "asian_pi_2020", "hisp_2020", "pct_white_2020", "pct_black_2020", "pct_native_2020", "pct_asian_pi_2020", "pct_hispanic_2020", "pov_idx", "haz_idx", "tcost_idx", "pct_poor_ns", "pct_nonwhite", "hh_pct_white_lt30ami", "hh_pct_black_lt30ami", "hh_pct_hisp_lt30ami", "hh_pct_ai_pi_lt30ami", "stusab", "state", "state_name", "county", "county_name", "tract"]
df_small_cleaned = df_il_cleaned[req_cols]

# save to .csv file
df_small_cleaned.to_csv("all_counties.csv", encoding="utf-8")

path_to_atlas = (
    script_dir
    / "../dap2-redlining/Data/Raw_Data/data_center_geodata/im3_open_source_data_center_atlas"
    / "im3_open_source_data_center_atlas.csv"
).resolve()
df_atlas = pd.read_csv(path_to_atlas)
df_atlas

# load atlas and tracts
df_atlas[df_atlas["state_abb"] == "IL"]
df_small_cleaned = df_small_cleaned.merge(df_atlas, left_on="county_name", right_on="county", how="inner", indicator=True)
tracts_path = (
    script_dir
    / "../dap2-redlining/Data/Derived_Data/tl_2025_17_tract"
    / "tl_2025_17_tract.shp"
).resolve()
tracts = gpd.read_file(tracts_path)

# merge on geoid
tracts["GEOID"] = tracts["GEOID"].astype(int)
gdf_merged = tracts.merge(df_small_cleaned, left_on="GEOID", right_on="geoid", how="inner")
gdf_merged
