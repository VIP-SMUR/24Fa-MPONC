# config.py

# Layer handling
# https://www.census.gov/cgi-bin/geo/shapefiles/index.php
ZIP_URLS = [
    "https://www2.census.gov/geo/tiger/TIGER2010/TRACT/2010/tl_2010_13_tract10.zip", # GA Census tracts [2010]
    # "https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_13_tract.zip" # GA Census tracts [2020]
    "https://www2.census.gov/geo/tiger/TIGER2010/COUNTY/2010/tl_2010_13_county10.zip" # GA Counties [2010]
    #,"https://www2.census.gov/geo/tiger/TIGER2020/COUNTY/tl_2020_us_county.zip" # US Nationwide Counties [2020]
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
# https://data.census.gov/table/ACSST5Y2010.S1903?q=s1903%202010&g=050XX00US13089$1400000,13121$1400000
# [349 regions]
ECONOMIC_URL = "https://data.census.gov/api/access/table/download?download_id=6fad78b0ac510efbe0f426059c1394dfc06eb60dc6feabc66622be2b05a0048c"
ECONOMIC_DATA_SKIP_ROWS = [1]
ECONOMIC_DATA_COL = "S1903_C02_001E" # Name of 'Income' data column
# "-" label indicates either:
# 1) no sample observations or too few sample observations were available to compute an estimate
# 2) a ratio of medians cannot be calculated because one or both of the median estimates falls in the lowest or upper interval of an open-ended distribution

# TOTAL POPULATION
# https://data.census.gov/table/ACSDT5Y2022.B01003?q=B01003&g=050XX00US13089$1400000,13121$1400000
# [349 regions]
POPULATION_URL = "https://data.census.gov/api/access/table/download?download_id=4633c4c26713411721d6ab3ea6301d2048efb597bbd910dfc5783a9be347b400" 
POPULATION_DATA_SKIP_ROWS = [1, 2]
POPULATION_DATA_COL = "B01003_001E" # Name of 'Population' data column


""" List of regions to simulate """
# County FIPS codes: https://www.census.gov/library/reference/code-lists/ansi/2010.html
ID_LIST = [
    ('13121', True) #Fulton County  
    ,('13089', True) #Dekalb County
]

""" ID's of all 'Beltline' relations from Open Street Map """
RELATION_IDS = [8408433, 13048389]

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
RHO_L = [2] # House capacity                                             # [1, 2, 4, 8] rho (house capacity)
ALPHA_L = [0.25] # Prioritize proximity vs. community    # [0.25, 0.75] lambda (agent preference; proximity vs. community)
EPSILON = 1e-3 # Rate of learning
T_MAX_RANGE = 1 # Total timesteps                               [20000] 
BENCHMARK_INTERVALS = 1 # Benchmark interval
NUM_AGENTS = 200 # Number of agents

""" Flags """
RUN_EXPERIMENTS = False  # RUN SIMULATION?
RUN_CALIBRATION = True # RUN CALIBRATION?
PLOT_CITIES = False      # PLOT SIMULATION?
PLOT_FOLIUM = False        # Create Folium graph of t_max?
viewData = False        # View GDF info + more?
viewAmenityData = False # View amenity counts?

""" Visualization Settings """
COLORBAR_NUM_INTERVALS = 20 # Number of distinct colors to show in visualization
DPI = 9600 # DPI resolution of MatPlotLib graphs

""" GIF Settings """
GIF_FRAME_DURATION = 100 # Millseconds
GIF_NUM_PAUSE_FRAMES = 15 # Number of repeat frames to show upon GIF completion

""" Multiprocessing Settings - number of CPU's """
N_JOBS = -1

""" Geographic key (name) """
CTY_KEY = 'Georgia'
