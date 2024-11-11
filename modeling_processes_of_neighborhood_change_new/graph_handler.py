# graph_handler

import osmnx as ox
import networkx as nx
import pickle
from tqdm import tqdm
from config import ID_LIST
import pandas as pd
from gdf_handler import print_overlaps

# =========================
# GRAPH FILE INITIALIZATION
# =========================
def create_graph(GA_gdf):
    valid_IDS = set(GA_gdf['ID'])  # Set of valid IDS
    used_IDS = []  # List to store valid IDS being used for simulation
    invalid_IDS = []  # List to store invalid IDS
    gdf_sub_array = []  # List containing each IDS GeoDataFrame

    for ID, _ in tqdm(ID_LIST, desc="Filtering for IDs", unit="ID"):
        if ID in valid_IDS:
            # Filter GA_gdf for the current ID
            gdf_sub = GA_gdf[GA_gdf['ID'] == ID]
            gdf_sub_array.append(gdf_sub)
            used_IDS.append(ID)
        else:
            invalid_IDS.append(ID)
    
    # Concatenate regions
    if gdf_sub_array:
        gdf_combined = pd.concat(gdf_sub_array, ignore_index=True)
        # Check for overlaps
    else:
        raise ValueError("No valid ID's found.")
    
    # Combines all polygons within each region
    combined_shape = gdf_combined.geometry.union_all()
    
    print("Generating graph from OSMnx...")
    
    # Generate the graph
    g = ox.graph_from_polygon(combined_shape, network_type='drive', simplify=True)  # Roadmap of GA (networkx.MultiDiGraph)
    g = g.subgraph(max(nx.strongly_connected_components(g), key=len)).copy()  # Ensures all nodes are connected
    g = nx.convert_node_labels_to_integers(g)  # Converts nodes to integers
    
    if invalid_IDS:
        print(f"Invalid IDs: {invalid_IDS}")
    return g, used_IDS

def save_graph(g, used_IDS, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump({'graph': g, 'ID': used_IDS}, file)
    print(f"Graph saved to cache: '{file_path}'.\n")

def load_graph(file_path, GA_gdf):
    
    gdf_sub_array = []
    
    # Check for overlaps
    for ID, _ in ID_LIST:
        if ID in set(GA_gdf['ID']):
            gdf_sub = GA_gdf[GA_gdf['ID'] == ID]
            gdf_sub_array.append(gdf_sub)
    gdf_combined = pd.concat(gdf_sub_array, ignore_index=True)
            
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    g = data['graph']
    saved_IDs = data['ID']
    print(f"Loading graph '{file_path.name}' from cache...\n")
    return g, saved_IDs