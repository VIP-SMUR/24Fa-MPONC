# helper.py
from config import ZIP_URLS, T_MAX_RANGE, BENCHMARK_INTERVALS
from pathlib import Path
import os
import numpy as np
import osmnx as ox
import pickle

""" Directories """
BASE_DIR = Path.cwd()
DATA_DIR = BASE_DIR / 'data'
FIGURES_DIR = BASE_DIR / 'figures'
FOLIUM_DIR = FIGURES_DIR / 'folium'
PLT_DIR = FIGURES_DIR / 'matplotlib'
GIFS_CACHE_DIR = FIGURES_DIR / 'gifs'
CACHE_DIR = BASE_DIR / 'cache'
AMTS_DENS_CACHE_DIR = CACHE_DIR / 'amts_dens'
CENTROID_DIST_CACHE_DIR = CACHE_DIR / 'centroid_distances'
OSMNX_CACHE_DIR = CACHE_DIR / 'osmnx_cache'
FIGURE_PKL_CACHE_DIR = CACHE_DIR / 'pkl_figures'
GDF_CACHE_DIR = CACHE_DIR / 'gdfs'
LAYER_CACHE_DIR = CACHE_DIR / 'layers'
SAVED_IDS_CACHE_DIR = CACHE_DIR / 'saved_ids'
CENSUS_DATA_CACHE_DIR = CACHE_DIR / 'census_data'

for directory in [
    FOLIUM_DIR, PLT_DIR, SAVED_IDS_CACHE_DIR, GIFS_CACHE_DIR, 
    LAYER_CACHE_DIR, GDF_CACHE_DIR, CACHE_DIR, DATA_DIR, FIGURES_DIR, AMTS_DENS_CACHE_DIR, 
    CENTROID_DIST_CACHE_DIR, OSMNX_CACHE_DIR, FIGURE_PKL_CACHE_DIR, CENSUS_DATA_CACHE_DIR
    ]:
    os.makedirs(directory, exist_ok=True)
    
""" Create T_MAX_L """
num_benchmarks = int(T_MAX_RANGE/BENCHMARK_INTERVALS)
T_MAX_L = np.linspace(BENCHMARK_INTERVALS, T_MAX_RANGE, num_benchmarks, dtype=int)

""" Set OSMNX cache location """
ox.settings.cache_folder = OSMNX_CACHE_DIR    # Set OSMnx cache directory

""" File names """
SAVED_IDS_FILE = SAVED_IDS_CACHE_DIR / f"saved_IDS.pkl"
GDF_CACHE_FILENAME = GDF_CACHE_DIR / "gdf.gpkg"
GDF_NUM_GEOMETRIES_FILE = GDF_CACHE_DIR / "num_geometries"
GDF_NUM_GEOMETRIES_INDIVIDUAL_FILE = GDF_CACHE_DIR / "num_geometries_individual"
GRAPH_FILE = CACHE_DIR / f"graph.pkl"
ECONOMIC_DATA_FILENAME = CENSUS_DATA_CACHE_DIR / f"economic_data.xlsx"
POPULATION_DATA_FILENAME = CENSUS_DATA_CACHE_DIR / f"population_data.xlsx"

""" Layer management """
#Dictionaries to store layer variables
layer_zip_filenames = {}
layer_extract_filenames = {}
shapefile_names = {}
gdf_cache_filenames = {}
#Generate variables for above
for i in range(1, len(ZIP_URLS) + 1):
    layer_zip_filenames[i] = f"layer_{i}.zip"
    layer_extract_filenames[i] = layer_zip_filenames[i].rsplit('.', 1)[0]
    gdf_cache_filenames[i] = GDF_CACHE_DIR / f"gdf_{i}.gpkg"