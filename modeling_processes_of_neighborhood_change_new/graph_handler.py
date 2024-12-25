# graph_handler

import osmnx as ox
import networkx as nx
import pickle
from helper import GRAPH_FILE

# =========================
# GRAPH FILE INITIALIZATION
# =========================

def create_graph(gdf):
    """ Initialize graph from Geodataframe"""
    # Combine all shapes
    combined_gdf = gdf.unary_union
    
    # Generate the graph from the combined geometry
    g = ox.graph_from_polygon(combined_gdf, network_type='drive', simplify=True
    )
    
    # Ensure the graph is strongly connected
    if not nx.is_strongly_connected(g):
        print("Graph is not strongly connected. Extracting the largest strongly connected component.")
        g = g.subgraph(
            max(nx.strongly_connected_components(g), key=len)
        ).copy()
    
    # Convert node labels to integers
    g = nx.convert_node_labels_to_integers(g)
    return g

def save_graph(g, file_path=GRAPH_FILE):
    """ Save graph to cache """
    with open(file_path, 'wb') as file:
        pickle.dump(g, file)
    print(f"Combined graph saved to '{file_path}'.")

def load_graph(file_path=GRAPH_FILE):
    """ Load graph from cache """
    with open(file_path, 'rb') as file:
        g = pickle.load(file)
    return g