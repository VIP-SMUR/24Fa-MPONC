import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
import pickle

from City import City
from Centroid import Centroid
from Agent import Agent

# Initialize list of centroids
centroids = []
centroids.append(Centroid(0.0, 0.0, 'RDA/Cascade', True))
centroids.append(Centroid(0.0, 0.0, 'Pittsburgh/Peoplestown', True))
centroids.append(Centroid(0.0, 0.0, 'Boulevard Crossing', True))
centroids.append(Centroid(0.0, 0.0, 'Memorial Drive/Glenwood', True))
centroids.append(Centroid(0.0, 0.0, 'Freedom Parkway', True))
centroids.append(Centroid(0.0, 0.0, 'Virginia Highlands/Ansley', True))
centroids.append(Centroid(0.0, 0.0, 'Peachtree/Collier', True))
centroids.append(Centroid(0.0, 0.0, 'Upper Westside/Northside', True))
centroids.append(Centroid(0.0, 0.0, 'Simpson/Hollowell', True))
centroids.append(Centroid(0.0, 0.0, 'Upper Marietta/Westside Park', True))

# [OLD] Load city map to establish nodes
# WE NEED GRAPH 'g' WITH CENTROIDS
'''
load_g = True
if not load_g:
    gdf = gpd.read_file('./data/tl_2022_us_zcta520/tl_2022_us_zcta520.shp')
    gdf = gdf[gdf['ZCTA5CE20'] == '11206']
    shape = gdf.iloc[0].geometry
    
    #g is graph
    g = ox.graph_from_polygon(shape, network_type='drive', simplify=True)
    g = g.subgraph(max(nx.strongly_connected_components(g), key=len)).copy()
    g = nx.convert_node_labels_to_integers(g)
    with open('./data/williamsburg.pkl', 'wb') as file:
        pickle.dump(g, file)
else:
    with open('./data/williamsburg.pkl', 'rb') as file:
        g = pickle.load(file)
               
amts = [ox.nearest_nodes(g, lon, lat) for lon, lat, _ in centroids] #switched lon, lat order in for loop
'''

# SIMULATION PRE-DETERMINED PARAMETERS

rho_l = [1, 2, 4, 8] # (for each iteration) rho-house capacity
alpha_l = [0.25, 0.75] # (for each iteration) lambda-transit access vs. community value
t_max_l = [5000, 10000, 15000, 20000] # (for each iteration) timesteps
tau = 0.5 # inequality factor in Lorentz curve

cty_key = 'Atlanta' # [changed 'williamsburg' to 'Atlanta']

# RUN SIMULATION?
run_experiments = True

# PLOT SIMULATION?
plot_cities = True

n = g.number_of_nodes() - len(amts) # n = number of housing nodes (total nodes - transit nodes)
if run_experiments:
    for rho in rho_l: # iterate through iterations
        for alpha in alpha_l: # iterate through iterations

            np.random.seed(0)

            city = City(g, rho=rho) 
            city.set_amts(amts)

            agt_dows = np.diff([1 - (1 - x) ** tau for x in np.linspace(0, 1, n + 1)]) #establish endowment distribution
            
            agts = [Agent(i, dow, city, alpha=alpha) for i, dow in enumerate(agt_dows)] #initialize list of all agents

            city.set_agts(agts)
            city.update()

            for t in range(max(t_max_l)):
                print('t: {0}'.format(t))
                for a in agts:
                    a.act()
                city.update()
                for a in agts:
                    a.learn()

                if t + 1 in t_max_l:

                    for a in city.agts:
                        a.avg_probabilities = a.tot_probabilities / (t + 1)

                    with open('./data/{0}_{1}_{2}_{3}.pkl'.format(cty_key, rho, alpha, t + 1), 'wb') as file:
                        pickle.dump(city, file)

if plot_cities:
    for rho in rho_l: 
        for alpha in alpha_l:
            for t_max in t_max_l:
                with open('./data/{0}_{1}_{2}_{3}.pkl'.format(cty_key, rho, alpha, t_max), 'rb') as file:
                    city = pickle.load(file)
                cmap = 'YlOrRd'
                figkey = './{0}_{1}_{2}_{3}'.format(cty_key, rho, alpha, t_max)
                city.plot(cmap=cmap, figkey=figkey)
