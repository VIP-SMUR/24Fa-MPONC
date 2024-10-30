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
    ('HS6443060', False),   # Lakeside HS
    ('1315172', False),     # Chamblee City
    ('1368516', False),     # Sandy Springs City
    ('HS6331069', False),   # Wheeler HS
    ('HS6334066', False),   # Pebblebrook hS
    ('1317776', False),     # College Park
    ('HS6312052', False),   # North Clayton HS
    ('HS6310115', False),   # Drew HS
    ('HS6311054', False),   # Forest Park HS
    ('HS6314058', False),   # Morrow HS
    ('HS6442054', False),   # Columbia HS
    
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
    
    # # Housing Districts
    # ('HOUSE081', False),
    # ('HOUSE087', False),

    ('1304000', False)      # Atlanta City - KEEP AS LAST ELEMENT (for graphing purposes)
]

# Simulation Parameters
RHO_L = [1]          # [1, 2, 4, 8] for each iteration (rho-house capacity)
ALPHA_L = [0.25]     # [0.25, 0.75] for each iteration (lambda - centroid proximity vs. community value)
T_MAX_L = [100]       # Benchmarks
NUM_AGENTS = 11      # Number of agents

# Flags
RUN_EXPERIMENTS = True  # RUN SIMULATION?
PLOT_CITIES = True      # PLOT SIMULATION?
PLOT_LIBRARY = 0        # 1 for matplotlib, else for Folium

# City Key (name)
CTY_KEY = 'Georgia'