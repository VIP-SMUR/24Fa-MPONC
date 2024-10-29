# graph_handler.PythonFinalizationError

import osmnx as ox
import networkx as nx
import pickle
from tqdm import tqdm
from config import GRAPH_FILE
import pandas as pd

# =========================
# GRAPH FILE INITIALIZATION
# =========================

def create_graph(GA_gdf, GEOIDS):
    valid_GEOIDS = set(GA_gdf['GEOID'])  # Set of valid GEOIDs
    used_GEOIDS = []  # List to store valid GEOIDs being used for simulation
    invalid_GEOIDS = []  # List to store invalid GEOIDs
    gdf_sub_array = []  # List containing each GEOID's GeoDataFrame

    for geoid, _ in tqdm(GEOIDS, desc="Filtering for GEOIDs", unit="geoid"):
        if geoid in valid_GEOIDS:
            # Filter GA_gdf for the current GEOID
            gdf_sub = GA_gdf[GA_gdf['GEOID'] == geoid]
            gdf_sub_array.append(gdf_sub)
            used_GEOIDS.append(geoid)
        else:
            invalid_GEOIDS.append(geoid)
    
    # Concatenate GEOID regions
    if gdf_sub_array:
        gdf_combined = pd.concat(gdf_sub_array, ignore_index=True)
    else:
        raise ValueError("No valid GEOID's found.")
    
    # Combines all polygons within GEOID regions
    combined_shape = gdf_combined.geometry.unary_union  # More efficient than union_all
    
    print("Generating graph from OSMnx...")
    
    # Generate the graph
    g = ox.graph_from_polygon(combined_shape, network_type='drive', simplify=True)  # Roadmap of GA (networkx.MultiDiGraph)
    g = g.subgraph(max(nx.strongly_connected_components(g), key=len)).copy()  # Ensures all nodes are connected
    g = nx.convert_node_labels_to_integers(g)  # Converts nodes to integers
    
    print("Graph generated.")
    if invalid_GEOIDS:
        print(f"Invalid GEOIDs: {invalid_GEOIDS}")
    return g, used_GEOIDS

def save_graph(g, used_GEOIDS, file_path=GRAPH_FILE):
    with open(file_path, 'wb') as file:
        pickle.dump({'graph': g, 'GEOIDS': used_GEOIDS}, file)
    print(f"Graph saved to '{file_path}'.\n")

def load_graph(file_path=GRAPH_FILE):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    g = data['graph']
    saved_GEOIDS = data['GEOIDS']
    print(f"Graph loaded from '{file_path}'.")
    return g, saved_GEOIDS
