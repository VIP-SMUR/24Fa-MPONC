#helper.py
from config import ZIP_URLS
from pathlib import Path
import os

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
for directory in [LAYER_CACHE_DIR, GDF_CACHE_DIR, CACHE_DIR, DATA_DIR, FIGURES_DIR, AMTS_DENS_CACHE_DIR, CENTROID_DIST_CACHE_DIR, OSMNX_CACHE_DIR, FIGURE_PKL_CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

# Constants:
EPSILON = 1e-3
TAU = 0.5  # Inequality factor in Lorentz curve

# Dictionaries to store generated variables
zip_filenames = {}
extracted_names = {}
shapefile_names = {}
graph_filenames = {}
gdf_cache_filenames = {}

# Loop through num_layers
for i in range(1, len(ZIP_URLS) + 1):
    # Generate variable names
    zip_filenames[i] = f"layer_{i}.zip"
    extracted_names[i] = zip_filenames[i].rsplit('.', 1)[0]
    graph_filenames[i] = CACHE_DIR / f"graph.pkl"
    gdf_cache_filenames[i] = GDF_CACHE_DIR / f"gdf_{i}.gpkg"