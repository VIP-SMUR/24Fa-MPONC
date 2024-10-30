#helper.py
from config import ZIP_URLS
from pathlib import Path

# Directories
BASE_DIR = Path.cwd()

CACHE_DIR = Path("cache")
DATA_DIR = Path("data")
FIGURES_DIR = Path("figures")
CACHE_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

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
    graph_filenames[i] = CACHE_DIR / f"graph_{i}.pkl"
    gdf_cache_filenames[i] = CACHE_DIR / f"gdf_{i}.gpkg"
    