# graph_handler

from config import ID_LIST
import osmnx as ox
import networkx as nx
import pickle
import os

# =========================
# GRAPH FILE INITIALIZATION
# =========================
def create_graph(combined_gdf):
    
    used_IDS = []  # List to store valid IDS being used for simulation
    for ID, _ in (ID_LIST):
        used_IDS.append(ID)
    
    # Create and set OSMnx cache directory
    osmnx_cache_dir = os.path.join('cache', 'osmnx_cache')
    ox.settings.cache_folder = osmnx_cache_dir  # Set OSMnx cache directory
    
    combined_shape = combined_gdf.geometry.unary_union
    print("Generating graph from OSMnx...")
    
    # Generate graph
    g = ox.graph_from_polygon(combined_shape, network_type='drive', simplify=True)  # Roadmap of simulation region (networkx.MultiDiGraph)
    g = g.subgraph(max(nx.strongly_connected_components(g), key=len)).copy()  # Ensures all nodes are connected
    g = nx.convert_node_labels_to_integers(g)  # Converts nodes to integers

    return g, used_IDS
    
def save_graph(g, used_IDS, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump({'graph': g, 'ID': used_IDS}, file)
    print(f"Graph saved to cache: '{file_path}'.\n")

def load_graph(file_path):
    
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    g = data['graph']
    saved_IDs = data['ID']
    print(f"Loading graph from: '{file_path}'...\n")
    return g, saved_IDs