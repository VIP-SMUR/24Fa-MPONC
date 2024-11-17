# graph_handler

from config import N_JOBS
import osmnx as ox
import networkx as nx
import pickle
from joblib import Parallel, delayed

# =========================
# GRAPH FILE INITIALIZATION
# =========================

# Use multiprocessing to create graphs of districts independelty (for caching)
def create_all_graphs(gdfs):
    g_list = Parallel(n_jobs=N_JOBS, backend='loky')(
        delayed(create_graph)(gdf) for gdf in gdfs
    )

def create_graph(gdf):
    shape = gdf.geometry.unary_union
    print("Generating graph from OSMnx...")
    
    # Generate graph
    g = ox.graph_from_polygon(shape, network_type='drive', simplify=True)  # Roadmap of simulation region (networkx.MultiDiGraph)
    g = g.subgraph(max(nx.strongly_connected_components(g), key=len)).copy()  # Ensures all nodes are connected
    g = nx.convert_node_labels_to_integers(g)  # Converts nodes to integers

    return g
    
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