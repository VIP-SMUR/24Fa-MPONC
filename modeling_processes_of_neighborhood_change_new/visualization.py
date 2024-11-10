# visualization.py

from config import PLOT_LIBRARY, CTY_KEY, NUM_AGENTS
from helper import CACHE_DIR
import matplotlib.pyplot as plt
import time
import folium
import matplotlib as mpl
from helper import FIGURES_DIR
from folium import CircleMarker
from pathlib import Path
from branca.colormap import LinearColormap
import osmnx as ox
import numpy as np
import pickle

# =============================
# VISUALIZATION EXECUTION LOGIC
# =============================

def plot_city(rho, alpha, t_max, centroids, g, combined_gdf):
    # Graph title, file name, and file path
    figkey = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{t_max}"
    pickle_filename = f"{figkey}.pkl"
    pickle_path = CACHE_DIR / pickle_filename
    
    # Graphing logic
    if pickle_path.exists():
        with open(pickle_path, 'rb') as file:
            city = pickle.load(file)
            
        # Retrieve data for plotting:
        # City data
        df_data = city.get_data()
        # 'Avg Endowment' from csv to gdf
        combined_gdf = combined_gdf.merge(df_data[['ID', 'Avg Endowment']], on='ID', how='left')
    
        if PLOT_LIBRARY == 1:
            plot_matplotlib(centroids=centroids, city=city, cmap='YlOrRd', figkey=figkey, graph=g, gdf=combined_gdf)
        else:
            plot_folium(centroids=centroids, city=city, cmap='YlOrRd', figkey=figkey, graph=g, gdf=combined_gdf)
    else:
        print(f"Pickle file '{pickle_filename}' does not exist. Skipping plotting.")
    

# MATPLOTLIB GRAPHER
def plot_matplotlib(centroids, city, cmap='YlOrRd', figkey='city', graph=None, gdf=None):
    
    start_time = time.time()
    
    fig, ax = plt.subplots(figsize=(10, 10))

    ox.plot_graph(graph, ax=ax, node_color='black', node_size=10, edge_color='gray', edge_linewidth=1, show=False, close=False)

    # Plot GDF layer (region boundaries)
    gdf_plot = gdf.plot(column='Avg Endowment', ax=ax, cmap=cmap, alpha=0.6, edgecolor='black', legend=False)

    # Plot centroids locations (this comes after the graph to make sure they are visible on top)
    colors = np.where(city.beltline_array, 'palegreen', 'white')
    ax.scatter(city.lon_array, city.lat_array, color=colors, s=120, alpha=0.8, edgecolor='black', linewidth=0.5)

    # Display inhabitant populations at each node:
    for ID in range(len(centroids)):
        lon = city.lon_array[ID]
        lat = city.lat_array[ID]
        inhabitants = len(city.inh_array[ID])
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
    
    
# FOLIUM GRAPHER
def plot_folium(centroids, city, cmap='YlOrRd', figkey='city', gdf=None):
    
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
    for i, (lat, lon) in enumerate(zip(city.lat_array, city.lon_array)):
        beltline_status = city.beltline_array[i]
        color = 'red' if beltline_status else 'black'

        #[ATTRIBUTES]
        # name
        name = city.name_array[i]
        # pop
        inhabitants = len(city.inh_array[i])
        # amenity density
        amenity_density = city.amts_dens[i]
        # avg endowment
        if inhabitants > 0: # Latest population > 0
            avg_endowment = 100 * (np.mean([agent.dow for agent in city.inh_array[i]]))
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

    # Save Folium map.osm as HTML
    m.save(f"./figures/{figkey}_folium.html")
    end_time = time.time()
    
    FOLIUM_DIR = Path(FIGURES_DIR) / f"{figkey}_folium.html"
    print(f"Plotted and saved {FOLIUM_DIR.name} [{end_time - start_time:.2f} s]")