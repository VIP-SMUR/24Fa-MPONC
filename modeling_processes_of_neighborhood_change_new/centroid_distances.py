#centroid_distances.py

from config import N_JOBS
from helper import CENTROID_DIST_CACHE_DIR
import os
import osmnx as ox
import networkx as nx
import numpy as np
from joblib import Parallel, delayed
import hashlib
import pickle

def _hash(*args, **kwargs):
    """ Hash function """
    hasher = hashlib.md5()
    for arg in args:
        hasher.update(pickle.dumps(arg))
    for key, value in sorted(kwargs.items()):
        hasher.update(pickle.dumps((key, value)))
    return hasher.hexdigest()

def cached_centroid_distances(centroids, g, cache_dir=CENTROID_DIST_CACHE_DIR):
    """ Retrieve DISTANCES from cache or calculate for first time """
    # Create a unique hash for the current inputs
    centroids_coords = [(c[0], c[1]) for c in centroids]
    cache_key = f"centroid_distances_{_hash(*centroids_coords)}.npy"
    cache_path = os.path.join(cache_dir, cache_key)
    
    print(f"Number of centroids: {len(centroids)}")

    if os.path.exists(cache_path):
        print("Loading cached centroid distances...")
        distance_matrix = np.load(cache_path)
    else:
        distance_matrix = compute_centroid_distances(centroids, g)
        np.save(cache_path, distance_matrix)
        print(f"Centroid distances cached.")
    
    return distance_matrix

def compute_centroid_distances(centroids, g):
    """ Perform calculations for centroid distances with multiprocessing"""
    # Number of centroids
    n = len(centroids)
    
    # Map centroids to nearest node
    centroid_nodes = [ox.nearest_nodes(g, c[0], c[1]) for c in centroids]
    
    # Initialize distance matrix
    distance_matrix = np.zeros((n, n))
    
    def compute_distances_from_source(i):
        source_node = centroid_nodes[i]
        lengths = nx.single_source_dijkstra_path_length(g, source_node, weight='length')
        distances = []
        for j in range(n):
            target_node = centroid_nodes[j]
            distance = lengths.get(target_node, np.inf) # np.inf for disconnected centroids
            distances.append(distance)
        return distances
    
    # Parallel computation of distances
    distances_list = Parallel(n_jobs=N_JOBS, backend='loky')(
        delayed(compute_distances_from_source)(i) for i in range(n)
    )
    
    distance_matrix = np.array(distances_list)
    
    # Handle disconnected centroids by setting them to the maximum finite distance
    if np.isinf(distance_matrix).any():
        finite_max = np.max(distance_matrix[np.isfinite(distance_matrix)])
        distance_matrix[np.isinf(distance_matrix)] = finite_max
    
    # Normalize the distance matrix
    if distance_matrix.max() > 0:
        distance_matrix /= distance_matrix.max()
    
    return distance_matrix
