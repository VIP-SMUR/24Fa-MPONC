# config.py

'"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""'
'""""""""""""""""""" LAYER CONFIGURATION """""""""""""""""""'

'''
1. GA Census tracts [2020]
2. US Nationwide Counties [2020]
3. 
'''

ZIP_URLS = [
"https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_13_tract.zip"
,"https://www2.census.gov/geo/tiger/TIGER2020/COUNTY/tl_2020_us_county.zip"
]

# Name of 'ID' columns for respective shapefiles, to be renamed to 'Simulation_ID'
IDENTIFIER_COLUMNS = {
    1: 'GEOID',
    2: 'GEOID',
}

# Name of 'Name' columns for respective shapefiles, to be renamed to 'Simulation_Name'
NAME_COLUMNS = {
    1: 'NAMELSAD',
    2: 'NAMELSAD'
}

'""""""""""""""""""" LAYER CONFIGURATION """""""""""""""""""'
'"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""'

""" List of regions to simmulate """
ID_LIST = [
    # ARC BELTLINE GEOGRAPHIC BOUNDARIES
    ('13121', True) #Fulton County  
    ,('13089', True) #Dekalb County
]


""" Amenity filters """
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

""" Simulation Parameters """
RHO_L = [4]          # [1, 2, 4, 8] for each iteration (rho-house capacity)
ALPHA_L = [0.25]     # [0.25, 0.75] for each iteration (lambda - centroid proximity vs. community value)
T_MAX_RANGE = 10000 # [20000] Range of T_MAX_L
BENCHMARK_INTERVALS = 200 # [1000] Intervals at which to assign benchmark timesteps
NUM_AGENTS = 1000    # Number of agents

EPSILON = 1e-3 # Rate of learning
TAU = 0.5  # Inequality factor in Lorentz curve

""" Flags """
RUN_EXPERIMENTS = True  # RUN SIMULATION?
PLOT_CITIES = True      # PLOT SIMULATION?
PLOT_LIBRARY = 1        # 1 for matplotlib, else for Folium
viewData = True         # View amenity density and region distance?

""" Visualization Settings """
COLORBAR_NUM_INTERVALS = 20 # Number of distinct colors to show in visualization
DPI = 9600 # DPI resolution of MatPlotLib graphs

""" GIF Settings """
GIF_FRAME_DURATION = 100 # Millseconds
GIF_NUM_PAUSE_FRAMES = 15 # Number of repeat frames to show upon GIF completion

""" Multiprocessing Settings - number of CPU's """
N_JOBS = 24 # maximum

""" Geographic key (name) """
CTY_KEY = 'Georgia'
