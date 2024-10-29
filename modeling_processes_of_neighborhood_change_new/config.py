# config.py

from pathlib import Path

# =============
# CONFIGURATION
# =============

# URL of the file to download
ZIP_URL = "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/ACS_2022_Geographic_boundaries/FeatureServer/replicafilescache/ACS_2022_Geographic_boundaries_-7361254879251475346.zip"

# Name of zip folder
ZIP_FILENAME = "ACS_2022_Geographic_boundaries_-7361254879251475346.zip"
# Name of extracted folder (same as above, excluding '.zip')
EXTRACTED_NAME = ZIP_FILENAME.rsplit('.', 1)[0] 

# Format: ([GEOID], [IS_IN_BELTLINE])
GEOIDS = [
    ('BELTLINE01', True),
    ('BELTLINE02', True),
    ('BELTLINE03', True),
    ('BELTLINE04', True),
    ('BELTLINE05', True),
    ('BELTLINE06', True),
    ('BELTLINE07', True),
    ('BELTLINE08', True),
    ('BELTLINE09', True),
    ('BELTLINE10', True),
    ('HS6443070', False),   # Gresham Park
    ('HS6442055', False),   # Druid Hills
    ('1322052', False),     # Decatur city
    ('1325720', False),     # East Point
    ('HS6331054', False),   # Campbell HS
    ('1310944', False),     # BrookHaven City
    ('HS6440172', False),   # Panthersville
    ('1304000', False)      # Atlanta City - KEEP AS LAST ELEMENT (for graphing purposes)
]

# Constants:
EPSILON = 1e-3
TAU = 0.5  # Inequality factor in Lorentz curve

# ========================
# PATH CONFIGURATIONS
# ========================

# Path to current directory
BASE_DIR = Path.cwd()
# Path to data folder
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)  # Create 'data' directory if it doesn't exist

# Path to figures folder
FIGURES_DIR = BASE_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)  # Create 'figures' directory if it doesn't exist

# Path to cache folder
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)  # Create 'cache' directory if it doesn't exist

# Cached Files
GA_GDF_CACHE_FILE_NAME = "GA_gdf.gpkg"
GA_GDF_CACHE_FILE = DATA_DIR / GA_GDF_CACHE_FILE_NAME

GRAPH_FILE_NAME = "GA_graph.pkl"
GRAPH_FILE = DATA_DIR / GRAPH_FILE_NAME

# ========================
# SIMULATION PARAMETERS
# ========================

# Pre-determined Parameters
RHO_L = [1, 2, 4, 8]         # [1, 2, 4, 8] for each iteration (rho-house capacity)
ALPHA_L = [0.25, 0.75]    # [0.25, 0.75] for each iteration (lambda - centroid proximity vs. community value)
T_MAX_L = [200]     # [5000, 10000, 15000, 20000] for each iteration (timesteps)

NUM_AGENTS = 150    # Number of agents

# Flags
RUN_EXPERIMENTS = True  # RUN SIMULATION?
PLOT_CITIES = True      # PLOT SIMULATION?
PLOT_LIBRARY = 1        # 1 for matplotlib, else for Folium

# City Key (name)
CTY_KEY = 'Georgia'
