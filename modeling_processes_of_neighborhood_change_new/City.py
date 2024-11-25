# City.py

import numpy as np
import pandas as pd
import osmnx as ox

# ==========
# CITY CLASS
# ==========

class City:
    
    # CONSTRUCTOR
    def __init__(self, centroids, g, amts_dens, centroid_distances, rho, geo_id_to_income):
        ''' Initialize a City instance '''
        self.rho = rho  # house capacity
        self.centroids = centroids  # centroids list
        self.g = g  # OSM graph
        self.n = len(centroids)
        
        # STORE ATTRIBUTES OF ALL CENTROIDS 
        self.lon_array = np.array([lon for lon, _, _, _, _ in centroids])  # Longitude
        self.lat_array = np.array([lat for _, lat, _, _, _ in centroids])  # Latitude
        self.name_array = [name for _, _, name, _, _ in centroids]  # Centroid region name
        self.in_beltline_array = np.array([in_beltline for _, _, _, in_beltline, _ in centroids], dtype=bool).astype(float)  # In Beltline?
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
        
        # Map GEO_ID to income
        self.geo_id_to_income = geo_id_to_income

    # Set agents and their endowments
    def set_agts(self, agts):
        self.agts = agts  # list of agents
        self.agt_dows = np.array([a.dow for a in self.agts])  # array of agent endowments

    # Update each node (cmt score, population)
    def update(self):   
        for index in range(self.n):  # For each centroid
            inhabitants = self.inh_array[index] # Centroid inhabitants
            pop = len(inhabitants)
            
            # Update population history
            self.pop_hist[index].append(pop)
            
            if pop > 0:  # Inhabited
                # UPDATE COMMUNITY SCORE (avg inhabitant dows, weighted by distance to other centroids)
                inhabitant_dows = np.array([a.dow for a in inhabitants])  # Array of endowments of node's inhabitants
                distances = self.centroid_distances[index, [a.u for a in inhabitants]]
                weights = (1 - distances) ** 2
                
                # Update Community history (average endowment)
                cmt = np.average(inhabitant_dows, weights=weights) 
                
                # Establish endowment threshold
                if pop < self.rho:
                    self.dow_thr_array[index] = 0.0
                else:
                    self.dow_thr_array[index] = np.partition(inhabitant_dows, -self.rho)[-self.rho]
                self.upk_array[index] = True
                
            else:  # If uninhabited
                self.dow_thr_array[index] = 0.0
                self.upk_array[index] = False
                cmt = 0.0

            # Update Community history and Community Score (average endowment)
            self.cmt_hist[index].append(cmt)
            self.cmt_array[index] = cmt

    # =====================
    # SAVE DATA TO CSV FILE
    # =====================
    def get_data(self):
        """
        Gather data for each centroid and return as a DataFrame, filtering for regions
        that have valid economic distribution data.

        Returns:
        - DataFrame: Data containing Centroid, Population, Avg Endowment, In Beltline, Amt Density
                    only for regions with valid economic data.
        """
        data = []  # Array storing data for each centroid
        avg_endowments = np.zeros(self.n)

        # First, identify valid GEO_IDs (those with income data)
        valid_geo_ids = {geo_id for geo_id in self.geo_id_to_income.keys()
                         if self.geo_id_to_income[geo_id] != "NA"}

        # Calculate average endowments only for regions with valid data
        for index in range(self.n):
            if self.id_array[index] in valid_geo_ids:
                population = len(self.inh_array[index])
                # Average Endowment
                if population > 0:
                    avg_endowment = (np.mean([agent.dow for agent in self.inh_array[index]]))
                else:
                    avg_endowment = 0.0
                avg_endowments[index] = avg_endowment

        # Filter out zero endowments before normalization
        nonzero_mask = avg_endowments != 0
        valid_endowments = avg_endowments[nonzero_mask]

        # Normalize avg_endowments using only valid data
        if len(valid_endowments) > 0:
            min_val = valid_endowments.min()
            max_val = valid_endowments.max()

            # Normalize endowments for all regions
            normalized_avg_endowments = np.zeros_like(avg_endowments)
            normalized_avg_endowments[nonzero_mask] = (valid_endowments - min_val) / (max_val - min_val)
        else:
            normalized_avg_endowments = np.zeros_like(avg_endowments)

        # Collect data only for valid regions
        for index in range(self.n):
            ID = self.id_array[index]

            # Skip if this region wasn't used in economic distribution
            if ID not in valid_geo_ids:
                continue

            # Name
            centroid_name = self.name_array[index]

            # Population
            population = len(self.inh_array[index])

            avg_endowment = normalized_avg_endowments[index]

            # In Beltline?
            in_beltline = self.in_beltline_array[index]

            # Amenity Density
            amenity_density = self.amts_dens[index]

            # Expected income (2010 median income data)
            expected_income = self.geo_id_to_income[ID]  # We know it exists due to filtering

            data.append({
                'Simulation_ID': ID,
                'Centroid': centroid_name,
                'Population': population,
                'Avg Income': avg_endowment,
                'Expected Income': expected_income,
                'Avg Endowment Normalized': normalized_avg_endowments[index],
                'In Beltline': in_beltline,
                'Amt Density': round(amenity_density, 2)
            })

        df = pd.DataFrame(data)

        return df
