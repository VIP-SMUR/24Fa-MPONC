# City.py

import numpy as np
import pandas as pd
import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

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
        self.g = g  # OSMnx map
        self.n = len(centroids)
        
        # STORE ATTRIBUTES OF ALL CENTROIDS 
        self.lat_array = np.array([lat for _, lat, _, _ in centroids])  # Latitude
        self.lon_array = np.array([lon for lon, _, _, _ in centroids])  # Longitude
        self.beltline_array = np.array([beltline for _, _, _, beltline in centroids], dtype=bool).astype(float)  # In Beltline?
        self.name_array = [name for _, _, name, _ in centroids]  # Centroid region name
        
        self.inh_array = [set() for _ in range(self.n)]  # Array of sets - each set contains Agent inhabitants
        self.dow_thr_array = np.zeros(self.n)  # Endowment threshold
        self.upk_array = np.zeros(self.n, dtype=bool)  # Upkeep score
        self.cmt_array = np.zeros(self.n)  # Community score
        
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

            # Update Community history (average endowment)
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
        
        for ID in range(self.n):
            # Name
            centroid_name = self.name_array[ID]
            
            # Population
            population = len(self.inh_array[ID])
            
            # Average Endowment
            if population > 0:
                avg_endowment = 100 * (np.mean([agent.dow for agent in self.inh_array[ID]]))
            else:
                avg_endowment = 0.0
                
            # In Beltline?
            in_beltline = self.beltline_array[ID]
            
            # Amenity Density
            amenity_density = self.amts_dens[ID]

            data.append({
                'Centroid': centroid_name,
                'Population': population,
                'Avg Endowment': round(avg_endowment, 2),
                'In Beltline': in_beltline,
                'Amt Density': round(amenity_density, 2)
            })
        df = pd.DataFrame(data)
        return df
            
    # ==================
    # CITY PLOTTING CODE
    # ==================
    def plot(self, cmap='YlOrRd', figkey='city', graph=None):
        """
        Plot the city visualization including the graph, agents, and centroids.

        Parameters:
        - cmap (str): Colormap for the heatmap.
        - figkey (str): Identifier for the figure filename.
        - graph (Graph): NetworkX graph to plot.
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        if graph:
            ox.plot_graph(graph, ax=ax, node_color='black', node_size=10, edge_color='gray', edge_linewidth=1, show=False, close=False)

        # Prepare agent data
        agent_lats = np.array([self.lat_array[agent.u] for agent in self.agts])
        agent_lons = np.array([self.lon_array[agent.u] for agent in self.agts])
        agent_wealths = np.array([agent.dow for agent in self.agts])

        # Population density heatmap
        heatmap, xedges, yedges = np.histogram2d(agent_lons, agent_lats, bins=30)
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        ax.imshow(heatmap.T, extent=extent, origin='lower', cmap=cmap, alpha=0.5)

        # Plot agents with wealth-based marker sizes
        norm = Normalize(vmin=agent_wealths.min(), vmax=agent_wealths.max())
        marker_sizes = 50 + 150 * norm(agent_wealths)
        sc = ax.scatter(agent_lons, agent_lats, c=agent_wealths, s=marker_sizes, cmap='coolwarm', alpha=0.7, edgecolor='red')

        # Plot centroids locations (this comes after the graph to make sure they are visible on top)
        colors = np.where(self.beltline_array, 'yellow', 'white')
        ax.scatter(self.lon_array, self.lat_array, color=colors, s=100, alpha=0.7, edgecolor='black')
            
        for ID in range(self.n):    
            lon = self.lon_array[ID]
            lat = self.lat_array[ID]
            # Display inhabitant populations at each node:
            inhabitants = len(self.inh_array[ID])
            ax.text(lon, lat, str(inhabitants), fontsize=9, ha='center', va='center', color='black')

        # Add color bar for wealth
        cbar = plt.colorbar(sc, ax=ax, orientation='vertical', label='Wealth (dow)')

        # Labels and title
        ax.set_title(f"City Visualization: {figkey}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        # Legend
        ax.scatter([], [], c='yellow', s=100, label='Beltline Housing')
        ax.scatter([], [], c='white', s=100, label='Non-Beltline Housing')
        ax.scatter([], [], c='red', s=100, label='Agents')
        ax.legend(loc='upper right')

        plt.tight_layout()
        plt.savefig(f'./figures/{figkey}.pdf', format='pdf', bbox_inches='tight')
        plt.close()