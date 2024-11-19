#helper.py
from config import ZIP_URLS, T_MAX_RANGE, BENCHMARK_INTERVALS
from pathlib import Path
import os
import numpy as np
import osmnx as ox
import pickle

""" Directories """
BASE_DIR = Path.cwd()
CACHE_DIR = Path("cache")
DATA_DIR = Path("data")
FIGURES_DIR = Path("figures")
AMTS_DENS_CACHE_DIR = Path('cache/amts_dens')
CENTROID_DIST_CACHE_DIR = Path('cache/centroid_distances')
OSMNX_CACHE_DIR = Path('cache/osmnx_cache')
FIGURE_PKL_CACHE_DIR = Path('cache/pkl_figures')
GDF_CACHE_DIR = Path('cache/gdfs')
LAYER_CACHE_DIR = Path('cache/layers')
GIFS_DIR = Path('figures/gifs')
SAVED_IDS_DIR = Path('cache/saved_ids')
for directory in [SAVED_IDS_DIR, GIFS_DIR, LAYER_CACHE_DIR, GDF_CACHE_DIR, CACHE_DIR, DATA_DIR, FIGURES_DIR, AMTS_DENS_CACHE_DIR, CENTROID_DIST_CACHE_DIR, OSMNX_CACHE_DIR, FIGURE_PKL_CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)
    
""" Create T_MAX_L """
num_benchmarks = int(T_MAX_RANGE/BENCHMARK_INTERVALS)
T_MAX_L = np.linspace(BENCHMARK_INTERVALS, T_MAX_RANGE, num_benchmarks, dtype=int)

""" Set OSMNX cache location """
ox.settings.cache_folder = OSMNX_CACHE_DIR    # Set OSMnx cache directory

""" Name of cached saved_IDS file """
SAVED_IDS_FILE = SAVED_IDS_DIR / f"saved_IDS.pkl"

""" Name of cached graph file """
GRAPH_FILE = CACHE_DIR / f"graph.pkl"

""" Layer management """
#Dictionaries to store layer variables
zip_filenames = {}
extracted_names = {}
shapefile_names = {}
gdf_cache_filenames = {}
#Generate variables for above
for i in range(1, len(ZIP_URLS) + 1):
    zip_filenames[i] = f"layer_{i}.zip"
    extracted_names[i] = zip_filenames[i].rsplit('.', 1)[0]
    gdf_cache_filenames[i] = GDF_CACHE_DIR / f"gdf_{i}.gpkg"