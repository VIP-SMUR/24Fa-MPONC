# config.py

# Layer handling
ZIP_URLS = [
"https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_13_tract.zip" # GA Census tracts [2020]
,"https://www2.census.gov/geo/tiger/TIGER2020/COUNTY/tl_2020_us_county.zip" # US Nationwide Counties [2020]
]

# Name of 'ID' columns, to be renamed to 'Simulation_ID'
IDENTIFIER_COLUMNS = {
    1: 'GEOID',
    2: 'GEOID',
}

# Name of 'Name' columns, to be renamed to 'Simulation_Name'
NAME_COLUMNS = {
    1: 'NAMELSAD',
    2: 'NAMELSAD'
}

# Database to download data from: ACS 5-Year Estimates Detailed Tables - https://data.census.gov/advanced?g=040XX00US13
# [DATA USED TO INITIALIZE AGENT ENDOWMENTS]

# MEDIAN INCOME IN THE PAST 12 MONTHS (IN 2010 INFLATION-ADJUSTED DOLLARS) 
ECONOMIC_URL = "https://data.census.gov/api/access/table/download?download_id=6fad78b0ac510efbe0f426059c1394dfc06eb60dc6feabc66622be2b05a0048c"
ECONOMIC_DATA_SKIP_ROWS = [1]
ECONOMIC_DATA_COL = "S1903_C02_001E" # Name of 'Income' data column

# TOTAL POPULATION
POPULATION_URL = "https://data.census.gov/api/access/table/download?download_id=1cc6f201844c171e3f9f3a99d8a571de3232c8a360010f81ce8c98c076b797e0" 
POPULATION_DATA_SKIP_ROWS = [1, 2]
POPULATION_DATA_COL = "B01003_001E" # Name of 'Population' data column


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
RHO_L = [2]          # [1, 2, 4, 8] for each iteration (rho-house capacity)
ALPHA_L = [0.25]     # [0.25, 0.75] for each iteration (lambda - centroid proximity vs. community value)
T_MAX_RANGE = 2 # [20000] Range of T_MAX_L
BENCHMARK_INTERVALS = 1 # [1000] Intervals at which to assign benchmark timesteps
NUM_AGENTS = 1    # Number of agents

EPSILON = 1e-3 # Rate of learning

""" Flags """
RUN_EXPERIMENTS = True  # RUN SIMULATION?
PLOT_CITIES = True      # PLOT SIMULATION?
PLOT_LIBRARY = 1        # 1 for matplotlib, else for Folium
viewData = False         # View GDF's, ameniti counts, ?

""" Visualization Settings """
COLORBAR_NUM_INTERVALS = 20 # Number of distinct colors to show in visualization
DPI = 9600 # DPI resolution of MatPlotLib graphs

""" GIF Settings """
GIF_FRAME_DURATION = 100 # Millseconds
GIF_NUM_PAUSE_FRAMES = 10 # Number of repeat frames to show upon GIF completion

""" Multiprocessing Settings - number of CPU's """
N_JOBS = -1

""" Geographic key (name) """
CTY_KEY = 'Georgia'
