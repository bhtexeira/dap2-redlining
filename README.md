# Data Center Impact on Illinois

Affirmatively Furhering Fair Housing Data and Mapping Tool data: https://uchicago.box.com/s/hu6l6g8rdhkxjlly80gq8tgp37fqpgek <br>
use the AFFH_tract_AFFHT0007_December2024.csv file and run the Data Cleaning for AFFH.qmd file to create the all_counties.csv file for use

## Setup

```bash
conda env create -f environment.yml
conda activate datacenter_analysis
```

## Project Structure

```
data/
  Raw_data/           # Raw data files
    im3_open_source_data_center_atlas.gpkg  # datacenter data
  Derived_data/       # Filtered data and output plots
    tl_2025_17_tract   # geodata
    all_counties.csv    # 2020 Illinois data on environmental conditions and demographics
code/
  preprocessing.py    # Filters data to illinois
  data_center_map.py       # Plots datacenters
```

## Usage

1. Run preprocessing to filter data:
   ```bash
   python code/preprocessing.py
   ```

2. Generate the datacenter plot:
   ```bash
   python code/data_center_map.py
   
