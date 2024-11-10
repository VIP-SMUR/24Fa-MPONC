# City.py

import numpy as np
import pandas as pd
import osmnx as ox

# ==========
# CITY CLASS
# ==========

class City:
    
    # CONSTRUCTOR
    def __init__(self, centroids, g, amts_dens, centroid_distances, rho=2):  # default rho (house capacity) == 2
        '''
        Initialize a City instance.
        '''
        self.rho = rho  # house capacity
        self.centroids = centroids  # centroids list
        self.g = g  # OSMnx map.osm
        self.n = len(centroids)
        
        # STORE ATTRIBUTES OF ALL CENTROIDS 
        self.lon_array = np.array([lon for lon, _, _, _, _ in centroids])  # Longitude
        self.lat_array = np.array([lat for _, lat, _, _, _ in centroids])  # Latitude
        self.name_array = [name for _, _, name, _, _ in centroids]  # Centroid region name
        self.beltline_array = np.array([beltline for _, _, _, beltline, _ in centroids], dtype=bool).astype(float)  # In Beltline?
        self.id_array = self.id_array = [id for _, _, _, _, id in centroids]  # ID
        
        self.inh_array = [set() for _ in range(self.n)]  # Array of sets - each set contains Agent inhabitants
        self.dow_thr_array = np.zeros(self.n)  # Endowment threshold
        self.upk_array = np.zeros(self.n, dtype=bool)  # Upkeep score
        self.cmt_array = np.zeros(self.n) # Community score
        
        self.pop_hist = [[] for _ in range(self.n)]  # Population history - list of lists 
        self.cmt_hist = [[] for _ in range(self.n)]  # Community score history - list of lists 
        
        self.node_array = np.array([ox.nearest_nodes(self.g, lon, lat) for lon, lat in zip(self.lon_array, self.lat_array)])
        
        # Amenity density and centroid distances
        self.amts_dens = amts_dens
        self.centroid_distances = centroid_distances

    # Set agents and their endowments
    def set_agts(self, agts):
        self.agts = agts  # list of agents
        self.agt_dows = np.array([a.dow for a in self.agts])  # array of agent endowments

    # Update each node (cmt score, population)
    def update(self):   
        for ID in range(self.n):  # For each centroid
            inhabitants = self.inh_array[ID]
            pop = len(inhabitants)
            
            # Update population history
            self.pop_hist[ID].append(pop)
            
            if pop > 0:  # Inhabited
                # UPDATE COMMUNITY SCORE (avg inhabitant dows, weighted by distance to other centroids)
                inhabitant_dows = np.array([a.dow for a in inhabitants])  # Array of endowments of node's inhabitants
                distances = self.centroid_distances[ID, [a.u for a in inhabitants]]
                weights = (1 - distances) ** 2
                
                # Update Community history (average endowment)
                cmt = np.average(inhabitant_dows, weights=weights) 
                
                # Establish endowment threshold
                if pop < self.rho:
                    self.dow_thr_array[ID] = 0.0
                else:
                    self.dow_thr_array[ID] = np.partition(inhabitant_dows, -self.rho)[-self.rho]
                self.upk_array[ID] = True
                
            else:  # If uninhabited
                self.dow_thr_array[ID] = 0.0
                self.upk_array[ID] = False
                cmt = 0.0

            # Update Community history and Community Score (average endowment)
            self.cmt_hist[ID].append(cmt)
            self.cmt_array[ID] = cmt

    # =====================
    # SAVE DATA TO CSV FILE
    # =====================
    def get_data(self):
        """
        Gather data for each centroid and return as a DataFrame.

        Returns:
        - DataFrame: Data containing Centroid, Population, Avg Endowment, In Beltline, Amt Density.
        """
        data = []  # Array storing data for each centroid
        
        for index in range(self.n):

            # ID
            ID = self.id_array[index]

            # Name
            centroid_name = self.name_array[index]
            
            # Population
            population = len(self.inh_array[index])
            
            # Average Endowment
            if population > 0:
                avg_endowment = 100 * (np.mean([agent.dow for agent in self.inh_array[index]]))
                avg_endowment = round(avg_endowment, 2)
            else:
                avg_endowment = 0.0
                
                
            # In Beltline?
            in_beltline = self.beltline_array[index]
            
            # Amenity Density
            amenity_density = self.amts_dens[index]

            data.append({
                'ID': ID,
                'Centroid': centroid_name,
                'Population': population,
                'Avg Endowment': avg_endowment,
                'In Beltline': in_beltline,
                'Amt Density': round(amenity_density, 2)
            })
        df = pd.DataFrame(data)
        return df