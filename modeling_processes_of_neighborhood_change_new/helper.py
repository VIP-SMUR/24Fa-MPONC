#helper.py
from config import ZIP_URLS, T_MAX_RANGE, BENCHMARK_INTERVALS, TARGET_ID_LIST
from pathlib import Path
import os
import numpy as np
import osmnx as ox

# Constants:
EPSILON = 1e-3
TAU = 0.5  # Inequality factor in Lorentz curve

# Create T_MAX_L from T_MAX_RANGE and BENCHMARK_INTERVALS
num_benchmarks = int(T_MAX_RANGE/BENCHMARK_INTERVALS)
T_MAX_L = np.linspace(BENCHMARK_INTERVALS, T_MAX_RANGE, num_benchmarks, dtype=int)

# Create list of used ID's
used_IDS = [ID for ID, _ in TARGET_ID_LIST]

# Directories
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
for directory in [GIFS_DIR, LAYER_CACHE_DIR, GDF_CACHE_DIR, CACHE_DIR, DATA_DIR, FIGURES_DIR, AMTS_DENS_CACHE_DIR, CENTROID_DIST_CACHE_DIR, OSMNX_CACHE_DIR, FIGURE_PKL_CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

# Name of pickled graph file
graph_file = CACHE_DIR / f"graph.pkl"

# Dictionaries to store generated variables
zip_filenames = {}
extracted_names = {}
shapefile_names = {}
gdf_cache_filenames = {}

# Loop through num_layers
for i in range(1, len(ZIP_URLS) + 1):
    # Generate variable names
    zip_filenames[i] = f"layer_{i}.zip"
    extracted_names[i] = zip_filenames[i].rsplit('.', 1)[0]
    gdf_cache_filenames[i] = GDF_CACHE_DIR / f"gdf_{i}.gpkg"