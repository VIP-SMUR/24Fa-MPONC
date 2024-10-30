# City.py

import numpy as np
import pandas as pd
import osmnx as ox
import matplotlib.pyplot as plt
import time
import folium
import matplotlib as mpl
from folium import CircleMarker
from helper import FIGURES_DIR
from pathlib import Path
from branca.colormap import LinearColormap


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
    
    
    # ==================
    # CITY PLOTTING CODE
    # ==================
    
    # Matplotlib:
    def plot_plt(self, cmap='YlOrRd', figkey='city', graph=None, gdf=None):
        start_time = time.time()
        
        fig, ax = plt.subplots(figsize=(10, 10))

        ox.plot_graph(graph, ax=ax, node_color='black', node_size=10, edge_color='gray', edge_linewidth=1, show=False, close=False)

        # Plot GDF layer (region boundaries)
        gdf_plot = gdf.plot(column='Avg Endowment', ax=ax, cmap=cmap, alpha=0.6, edgecolor='black', legend=False)

        # Plot centroids locations (this comes after the graph to make sure they are visible on top)
        colors = np.where(self.beltline_array, 'palegreen', 'white')
        ax.scatter(self.lon_array, self.lat_array, color=colors, s=120, alpha=0.8, edgecolor='black', linewidth=0.5)

        # Display inhabitant populations at each node:
        for ID in range(self.n):
            lon = self.lon_array[ID]
            lat = self.lat_array[ID]
            inhabitants = len(self.inh_array[ID])
            ax.text(lon, lat, str(inhabitants), fontsize=9, ha='center', va='center', color='black')

        # ScalarMappable for color bar implementation
        sm = mpl.cm.ScalarMappable(
            cmap=cmap,
            norm=plt.Normalize(vmin=gdf['Avg Endowment'].min(), vmax=gdf['Avg Endowment'].max())
        )

        # Add color bar
        cbar = fig.colorbar(sm, ax=ax, orientation='vertical', fraction=0.035, pad=0.02)
        cbar.set_label('Average Wealth', fontsize=12)

        # Labels and title
        ax.set_title(f"City Visualization: {figkey}", fontsize=14)

        plt.tight_layout()
        plt.savefig(f'./figures/{figkey}_matplotlib.pdf', format='pdf', bbox_inches='tight')
        plt.close()
        
        # Save graph to 'figures' folder
        PLT_DIR = Path(FIGURES_DIR) / f"{figkey}_matplotlib.pdf"
        end_time = time.time()
        print(f"Plotted and saved {PLT_DIR.name} [{end_time - start_time:.2f} s]")


    # Folium:
    def plot_folium(self, cmap='YlOrRd', figkey='city', graph=None, gdf=None):
        
        start_time = time.time()
        
        gdf = gdf.to_crs(epsg=32616)
                
        # Starting coords
        center_lat, center_lon = 33.7490, -84.3880  # Example coordinates (Atlanta, GA)
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

        # Colormap for GDF layer - shade polygons based on Avg Endowment
        min_value = gdf['Avg Endowment'].min()
        max_value = gdf['Avg Endowment'].max()
        colormap = plt.get_cmap(cmap)
        norm = plt.Normalize(vmin=min_value, vmax=max_value)
        color_mapper = lambda x: colormap(norm(x))
        
        # Convert matplotlib colors to hex for folium
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        
        # Define LinearColormap for folium
        folium_colormap = LinearColormap(
            colors=[rgb_to_hex(color_mapper(val)[:3]) for val in np.linspace(min_value, max_value, 256)],
            vmin=min_value,
            vmax=max_value,
            caption='Average Wealth'
        )
        
         # Customize GDF layer
        def style_function(feature):
            avg_endowment = feature['properties']['Avg Endowment']
            style_dict = {
                'color': 'black',     # Outline color of polygons
                'weight': 1,          # Outline weight
                'opacity': 0.3          # Outline opacity
            }
            if avg_endowment is None:
                style_dict['fillOpacity'] = 0  # Make polygon transparent
            else:
                style_dict['fillColor'] = folium_colormap(avg_endowment)
                style_dict['fillOpacity'] = 0.4  # Transparency
            return style_dict
        
        # Add the GDF layer (entirety of GA)
        folium.GeoJson(
            data=gdf,
            name='GDF Layer',
            style_function=style_function
        ).add_to(m)
        
        # Add colormap
        folium_colormap.add_to(m)

        # Add centroids as CircleMarker with beltline coloring
        for i, (lat, lon) in enumerate(zip(self.lat_array, self.lon_array)):
            beltline_status = self.beltline_array[i]
            color = 'red' if beltline_status else 'black'

            #[ATTRIBUTES]
            # name
            name = self.name_array[i]
            # pop
            inhabitants = len(self.inh_array[i])
            # amenity density
            amenity_density = self.amts_dens[i]
            # avg endowment
            if inhabitants > 0: # Latest population > 0
                avg_endowment = 100 * (np.mean([agent.dow for agent in self.inh_array[i]]))
                avg_endowment = round(avg_endowment, 2)
            else:
                avg_endowment = 0.0

            # Centroid pop-up customizer
            popup_text = f"""
                <div style="font-size: 14px; line-height: 1.6; max-width: 200px;">
                    <strong>{name}</strong><br><br>
                    <strong>Amt density:</strong> {amenity_density:.1f}/sqkm<br>
                    <strong>Population:</strong> {inhabitants}<br>
                    <strong>Wealth:</strong> {avg_endowment:.2f}
                </div>
            """

            CircleMarker(
                location=[lat, lon],
                color=color,
                fill=True,
                fill_opacity=0.8,
                radius=5,
                popup=folium.Popup(popup_text, max_width=250)
            ).add_to(m)

        # Add title and custom legend using HTML
        title_html = f'''
            <h3 align="center" style="font-size:20px"><b>City Visualization: {figkey}</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))

        legend_html = '''
             <div style="
             position: fixed; 
             bottom: 50px; left: 50px; width: 150px; height: 90px; 
             background-color: white; z-index:9999; font-size:14px;
             border:2px solid grey; padding: 10px;">
             <b>Legend</b><br>
             <i style="background: red; width: 20px; height: 20px; float: left; margin-right: 5px; opacity: 0.8;"></i>Beltline Housing<br>
             <i style="background: black; width: 20px; height: 20px; float: left; margin-right: 5px; opacity: 0.8;"></i>Non-Beltline Housing
             </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))

        # Save Folium map as HTML
        m.save(f"./figures/{figkey}_folium.html")
        end_time = time.time()
        
        FOLIUM_DIR = Path(FIGURES_DIR) / f"{figkey}_folium.html"
        print(f"Plotted and saved {FOLIUM_DIR.name} [{end_time - start_time:.2f} s]")
        