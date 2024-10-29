# amtsdens_distances.py

import osmnx as ox
import networkx as nx
import numpy as np
from tqdm import tqdm

# ================================================
# AMENITY DENSITY & CENTROID DISTANCE CALCULATIONS
# ================================================

def compute_amts_dens(GA_gdf, used_GEOIDS, viewData=True):
    # [AMENITY FILTER]
    tags = {'highway': 'bus_stop'}  # TODO: I don't think number of bus stops is accurate

    # Initialize empty arrays
    amenities = np.zeros(len(used_GEOIDS) - 1)
    areas_sqkm = np.zeros(len(used_GEOIDS) - 1)
    data_output = []

    # Iterate over each GEOID
    print()
    for index, geoid in enumerate(tqdm(used_GEOIDS[:-1], desc="Computing amenity densities", unit="GEOID")):
        name = GA_gdf.loc[GA_gdf['GEOID'] == geoid, 'Name'].iloc[0]
    
        # Extract polygon of current GEOID
        polygon = GA_gdf.loc[GA_gdf['GEOID'] == geoid, 'geometry'].union_all()

        # Collect amenities
        try:
            amenities[index] = len(ox.features_from_polygon(polygon, tags))
        except:  # No bus stops
            amenities[index] = 0
    
        # Area of current GEOID
        areas_sqkm[index] = GA_gdf.loc[GA_gdf['GEOID'] == geoid, 'Sqkm'].iloc[0]
    
        if viewData:
            data_output.append(f"{name:<40} {areas_sqkm[index]:>12.2f} {amenities[index]:>10}")
    
    # Amenity density (amenities / square kilometer)
    amts_dens = amenities / areas_sqkm
    
    # Normalize densities
    if np.max(amts_dens) > 0:
        amts_dens /= np.max(amts_dens)
    
    # Display data
    tqdm.write(f"{'[Region]':<40} {'[Area (sq km)]':>12} {'[# Amenities]':>10}")
    tqdm.write("\n".join(data_output))
    
    return amts_dens

def compute_centroid_distances(centroids, g, used_GEOIDS):
    n = len(centroids)
    
    # Map centroids to nearest node
    centroid_nodes = [ox.nearest_nodes(g, c[1], c[0]) for c in centroids]
    # 2D matrix of centroid-to-centroid distance
    distance_matrix = np.zeros((n, n))
    
    # Loop through each pair of nodes
    for i in tqdm(range(n), desc="Computing centroid distances"):
        source_node = centroid_nodes[i]
        for j in range(i, n):
            target_node = centroid_nodes[j]
            
            # Retrieve distance between source and target centroid nodes
            if i == j:
                distance = 0
            else:
                try:
                    distance = nx.shortest_path_length(g, source=source_node, target=target_node, weight='length')
                except nx.NetworkXNoPath:
                    distance = np.inf  # Assign infinity if no path exists
            distance_matrix[i][j] = distance
            distance_matrix[j][i] = distance  # Symmetric matrix
    
    # Handle infinities by setting them to the maximum finite distance
    if np.isinf(distance_matrix).any():
        raise ValueError("Distance matrix contains infinite values due to disconnected centroids.")
    
    # Normalize the distance matrix
    if distance_matrix.max() > 0:
        distance_matrix /= distance_matrix.max()
    
    return distance_matrix
