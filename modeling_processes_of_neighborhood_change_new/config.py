# config.py

# =====================================================
# ================== CONFIGURATION ====================

'''
[URLS]
1. Original geographic
2. Zip codes
3. Housing districts
'''
ZIP_URLS = [
 "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/ACS_2022_Geographic_boundaries/FeatureServer/replicafilescache/ACS_2022_Geographic_boundaries_-7361254879251475346.zip"
#,
#"https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/ACS 2022 Demographic Population GeoSplitJoined/FeatureServer/replicafilescache/ACS 2022 Demographic Population GeoSplitJoined_-5541227124544312025.zip"
#,
# "https://services1.arcgis.com/Ug5xGQbHsD8zuZzM/arcgis/rest/services/ACS 2022 Econ WorkerType GeoSplitJoined/FeatureServer/replicafilescache/ACS 2022 Econ WorkerType GeoSplitJoined_2117979253204255635.zip"
]

# Name of 'ID'' columns for respective shapefiles
IDENTIFIER_COLUMNS = {
    1: 'GEOID',
#    2: 'GEOID',
#    3: 'GEOID'
}

# Name of 'Name' columns for respective shapefiles
NAME_COLUMNS = {
    1: 'Name',
#    2: 'NAME',
#    3: 'NAME'
}

# ID's:
ID_LIST = [
    # ARC BELTLINE GEOGRAPHIC BOUNDARIES
    ('13121', True) #Fulton County
    #('13089', True), #Dekalb County
    
    # # ZCTA
    # ('30331', False),
    # ('30311', True),     
    # ('30327', False),    
    # ('30305', True),    
    # ('30315', True),     
    # ('30354', False),   
    # ('30318', True),    
    # ('30313', True),        
    # ('30303', True),
    # ('30308', True),   
    # ('30309', True),
    # ('30336', False),
    
     # Housing Districts
    #  ('HOUSE081', False),
    #  ('HOUSE087', False),
    #  ('1304000', False)
]

# Amenity filterS
AMENITY_TAGS = {
    'public_transport': ['platform', 'stop_position', 'station'],
    'highway': 'bus_stop',
    'railway': ['station', 'tram_stop', 'halt', 'subway_entrance'],
    'amenity': [
        'bus_station', 'train_station', 'airport',
        'government', 'university', 'place_of_worship', 'school',
        'civic_center', 'hospital'
    ],
    'shop': 'supermarket',
    'tourism': ['museum', 'hotel'],
    'building': ['apartments', 'house', 'service'],
    'landuse': ['residential', 'industrial'],
}

# Simulation Parameters
RHO_L = [4]          # [1, 2, 4, 8] for each iteration (rho-house capacity)
ALPHA_L = [0.25]     # [0.25, 0.75] for each iteration (lambda - centroid proximity vs. community value)
T_MAX_RANGE = 100 # [20000] Range of T_MAX_L
BENCHMARK_INTERVALS = 10 # [1000] Intervals at which to assign benchmark timesteps
NUM_AGENTS = 150    # Number of agents

# Flags
RUN_EXPERIMENTS = True  # RUN SIMULATION?
PLOT_CITIES = True      # PLOT SIMULATION?
PLOT_LIBRARY = 1        # 1 for matplotlib, else for Folium
viewData = True         # View amenity density and region distance?

# Graph Visualization Settings
COLORBAR_NUM_INTERVALS = 20 # Number of distinct colors to show in visualization
DPI = 2400 # DPI resolution of MatPlotLib graphs

# GIF Settings
GIF_FRAME_DURATION = 200 # Millseconds
GIF_NUM_PAUSE_FRAMES = 8 # Number of repeat frames to show upon GIF completion

# City Key (name)
CTY_KEY = 'Georgia'

# Number of CPU's to use for multiprocessing
N_JOBS = -1 # maximum