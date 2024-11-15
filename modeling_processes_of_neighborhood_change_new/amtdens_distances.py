# amtsdens_distances.py

from config import viewData
from helper import AMTS_DENS_CACHE_DIR, CENTROID_DIST_CACHE_DIR, OSMNX_CACHE_DIR
import os
import osmnx as ox
import networkx as nx
import numpy as np
import pickle
import hashlib
from tqdm import tqdm
from joblib import Parallel, delayed

def _hash(*args, **kwargs):
    """ Hash function """
    hasher = hashlib.md5()
    for arg in args:
        hasher.update(pickle.dumps(arg))
    for key, value in sorted(kwargs.items()):
        hasher.update(pickle.dumps((key, value)))
    return hasher.hexdigest()

def fetch_amenities(region_idx, region_polygon, tags, cache_dir=AMTS_DENS_CACHE_DIR):
    """ Fetch amenities for a single region. Utilize caching to avoid redundant API calls. """
    cache_key = f"region_{region_idx}_{_hash(tags=tags)}.npy"
    cache_path = os.path.join(cache_dir, cache_key)
    
    if os.path.exists(cache_path):
        # Fetch from cache
        with open(cache_path, 'rb') as f:
            amenities_count = pickle.load(f)
        return amenities_count
    else:
        # Calculate from OSM
        try:
            amenities = ox.features_from_polygon(region_polygon, tags=tags)
            amenities_count = len(amenities)
            # Save to cache
            with open(cache_path, 'wb') as f:
                pickle.dump(amenities_count, f)
        except:
            amenities_count = 0
    
    return amenities_count

def compute_amts_dens(gdf, tags):
    # Exclude Atlanta City from amts density calculations
    gdf = gdf[gdf['ID'] != '1304000'].reset_index(drop=True)
    
    amts_dens = np.zeros(len(gdf))
    amenities_counts = np.zeros(len(gdf))
    areas_sqkm = gdf['Sqkm'].values
    region_names = gdf['Name'].values

    print("Fetching amenities per region...")

    # Fetch amenities per region
    for idx, row in tqdm(gdf.iterrows(), total=len(gdf), desc="Regions"):
        region_polygon = row['geometry']
        amenities_count = fetch_amenities(idx, region_polygon, tags)
        amenities_counts[idx] = amenities_count
        if areas_sqkm[idx] > 0:
            amts_dens[idx] = amenities_count / areas_sqkm[idx]
        else:
            amts_dens[idx] = 0  # Avoid division by zero

    # Normalize densities
    max_density = amts_dens.max()
    if max_density > 0:
        amts_dens /= amts_dens.max()

    # View Data?
    if viewData:
        output_lines = [
            f"{name:<40} {area:>12.2f} {amt:>10}" for name, area, amt in zip(region_names, areas_sqkm, amenities_counts)
        ]
        print(f"{'[Region]':<40} {'[Area (sq km)]':>12} {'[# Amenities]':>10}")
        print("\n".join(output_lines))

    return amts_dens


def cached_centroid_distances(centroids, g, cache_dir=CENTROID_DIST_CACHE_DIR):
    """ Retrieve DISTANCES from cache or calculate for first time """
    # Create a unique hash for the current inputs
    centroids_coords = [(c[0], c[1]) for c in centroids]
    cache_key = f"centroid_distances_{_hash(*centroids_coords)}.npy"
    cache_path = os.path.join(cache_dir, cache_key)

    if os.path.exists(cache_path):
        print("Loading cached centroid distances...")
        distance_matrix = np.load(cache_path)
    else:
        distance_matrix = compute_centroid_distances(centroids, g)
        np.save(cache_path, distance_matrix)
        print(f"Centroid distances cached.")
    
    return distance_matrix

# Multiprocessing: Num CPU's
n_jobs = -1 #maximum

def compute_centroid_distances(centroids, g):
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
    print("Computing centroid distances...")
    distances_list = Parallel(n_jobs=n_jobs, backend='loky')(
        delayed(compute_distances_from_source)(i) for i in tqdm(range(n), desc="Centroids")
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

# Notes:
#   - Overpass API does not allow concurrent calls
#   - Limit to size of region to query amenities from; do region by region