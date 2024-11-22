# visualization.py

from config import PLOT_LIBRARY, CTY_KEY, NUM_AGENTS, COLORBAR_NUM_INTERVALS, DPI
from helper import FIGURE_PKL_CACHE_DIR, FIGURES_DIR, GRAPH_FILE, gdf_cache_filenames
from gdf_handler import load_gdf
from graph_handler import load_graph
import matplotlib.pyplot as plt
import time
import folium
import matplotlib as mpl
mpl.use('Agg') # Set non-interactive mpl backend
from helper import FIGURES_DIR
from folium import CircleMarker
from folium.plugins import MarkerCluster
from pathlib import Path
from branca.colormap import linear, StepColormap
import osmnx as ox
import numpy as np
import pickle

# =============================
# VISUALIZATION EXECUTION LOGIC
# =============================

def plot_city(rho, alpha, t_max, centroids):
    """ Main plot function """
    # Define graph title, file name, and file path
    figkey = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{t_max}"
    title = f"Timestep: {t_max}"
    pickle_filename = f"{figkey}.pkl"
    pickle_path = FIGURE_PKL_CACHE_DIR / pickle_filename
    
    # Don't pass large items as parameters - avoid pickling issues during multiprocessing (too big)
    g = load_graph(GRAPH_FILE)
    gdf, _, _ = load_gdf(gdf_cache_filenames)
    
    # Graphing logic
    if pickle_path.exists():
        with open(pickle_path, 'rb') as file:
            city = pickle.load(file)
            
        # Retrieve city data for plotting:
        df_data = city.get_data()
        
        # Set index
        gdf.set_index('Simulation_ID', inplace=True)
        df_data.set_index('Simulation_ID', inplace=True)
        
        # Join 'Avg Endowment' from csv to gdf
        gdf = gdf.join(df_data['Avg Endowment Normalized'], how='left').reset_index()
    
        # Plot with Matplotlib
        if PLOT_LIBRARY == 1:
            plot_matplotlib(
                centroids=centroids, 
                city=city, 
                title=title,
                figkey=figkey, 
                graph=g,
                gdf=gdf,
                )
        # Plot with Folium
        else:
            gdf = gdf.to_crs(epsg=32616)
            plot_folium(
                centroids=centroids, 
                city=city, 
                title=title,
                figkey=figkey, 
                graph=g, 
                gdf=gdf
            )
    else:
        print(f"Pickle file '{pickle_filename}' does not exist. Skipping plotting.")
    

# ================
# MATPLOTLIB GRAPH
# ================
""" Define global settings for matplotlib graphs for consistency """
# Global setup for colors and colormap
cmap_base = plt.get_cmap('YlOrRd')
fixed_colors = [cmap_base(i / (COLORBAR_NUM_INTERVALS - 1)) for i in range(COLORBAR_NUM_INTERVALS)]
discrete_cmap = mpl.colors.ListedColormap(fixed_colors)

# Fix boundaries and normalization
boundaries = np.linspace(0, 1, COLORBAR_NUM_INTERVALS + 1)
norm = mpl.colors.BoundaryNorm(boundaries, discrete_cmap.N, clip=True)

# Create ScalarMappable from above settings
global_sm = mpl.cm.ScalarMappable(cmap=discrete_cmap, norm=norm)
global_sm.set_array([])  # Fix color scale


def plot_matplotlib(centroids, city, title, figkey='city', graph=None, gdf=None):
    """ Matplotlib plotting function """
    start_time = time.time()
    
    fig, ax = plt.subplots(figsize=(10, 10))

    ox.plot_graph(graph, ax=ax, node_color='black', node_size=10, edge_color='gray', edge_linewidth=1, show=False, close=False)

    # Plot GDF layer (region boundaries)
    gdf.plot(column='Avg Endowment Normalized', ax=ax, cmap=discrete_cmap, alpha=0.6, edgecolor='black', legend=False)

    # Plot centroids locations (this comes after the graph to make sure they are visible on top)
    colors = np.where(city.in_beltline_array, 'palegreen', 'white')
    ax.scatter(city.lon_array, city.lat_array, color=colors, s=120, alpha=0.8, edgecolor='black', linewidth=0.5)

    # Display inhabitant populations at each node:
    for ID in range(len(centroids)):
        lon = city.lon_array[ID]
        lat = city.lat_array[ID]
        inhabitants = len(city.inh_array[ID])
        ax.text(lon, lat, str(inhabitants), fontsize=9, ha='center', va='center', color='black')
        
    # Use the global ScalarMappable for consistent colorbar
    cbar = fig.colorbar(global_sm, ax=ax, orientation='vertical', fraction=0.035, pad=0.02)
    cbar.set_label('Average Wealth', fontsize=12)

    # Labels and title
    ax.set_title(f"{title}", fontsize=14)

    plt.tight_layout()
    plt.savefig(f'./figures/{figkey}_matplotlib.pdf', format='pdf', bbox_inches='tight', dpi=DPI)
    plt.close()
    
    # Save graph to 'figures' folder
    PLT_DIR = Path(FIGURES_DIR) / f"{figkey}_matplotlib.pdf"
    end_time = time.time()
    print(f"Plotted and saved {PLT_DIR.name} [{end_time - start_time:.2f} s]")
    
    
# ============    
# FOLIUM GRAPH
# ============
def plot_folium(centroids, city, title, figkey='city', graph=None, gdf = None):
    """ Folium plotting function """
    start_time = time.time()
    
    # Center the map
    center_lat = np.mean(city.lat_array)
    center_lon = np.mean(city.lon_array)

    # Initialize folium graph
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Define LinearColormap for folium
    folium_colormap = linear.YlOrRd_09.scale(0, 1)
    folium_colormap.caption = 'Average Wealth'

    # Customize GDF layer
    def style_function(feature):
        avg_endowment = feature['properties']['Avg Endowment Normalized']
        return {
            'fillColor': folium_colormap(avg_endowment) if avg_endowment is not None else 'transparent',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.4 if avg_endowment is not None else 0,
    }

    # Add GDF layer
    folium.GeoJson(
        data=gdf,
        name='GDF Layer',
        style_function=style_function
    ).add_to(m)

    # Add colormap
    folium_colormap.add_to(m)

    # Initialize MarkerCluster
    marker_cluster = MarkerCluster().add_to(m)
    
    popup_texts = []
    
    # Add centroids as CircleMarker with beltline coloring
    for i, (lat, lon) in enumerate(zip(city.lat_array, city.lon_array)):
        
        #[ATTRIBUTES]
        
        # beltline status 
        beltline_status = city.in_beltline_array[i]
        color = 'red' if beltline_status else 'black'
        # name
        name = city.name_array[i]
        # pop
        inhabitants = len(city.inh_array[i])
        # amenity density
        amenity_density = city.amts_dens[i]
        # num amenities
        area = gdf.loc[gdf['Simulation_ID'] == city.id_array[i], 'Sqkm'].values
        area = area[0]
        num_amenities = amenity_density * area
        # avg endowment
        if inhabitants > 0: # Latest population > 0
            avg_endowment = gdf.loc[gdf['Simulation_ID'] == city.id_array[i], 'Avg Endowment Normalized'].values
            avg_endowment = avg_endowment[0] if len(avg_endowment) > 0 else 0.0
            avg_endowment = round(avg_endowment, 2)
        else:
            avg_endowment = 0.0

        # Centroid pop-up customizer
        popup_text = f"""
            <div style="font-size: 14px; line-height: 1.6; max-width: 200px;">
                <strong>{name}</strong><br><br>
                <strong>ID: </strong> {city.id_array[i]}<br>
                <strong>Amenities:</strong> {num_amenities:.0f}<br>
                <strong>Amt density:</strong> {amenity_density:.1f}/sqkm<br>
                <strong>Population:</strong> {inhabitants}<br>
                <strong>Wealth:</strong> {avg_endowment:.2f}
            </div>
        """
        
        popup_texts.append(popup_text)
        
        CircleMarker(
            location=[lat, lon],
            color=color,
            fill=True,
            fill_opacity=0.8,
            radius=5,
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(marker_cluster)

    # Add title and custom legend using HTML
    title_html = f'''
        <h3 align="center" style="font-size:20px"><b>City Visualization: {title}</b></h3>
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

    # Save Folium map.osm as HTML
    m.save(f"./figures/{figkey}_folium.html")