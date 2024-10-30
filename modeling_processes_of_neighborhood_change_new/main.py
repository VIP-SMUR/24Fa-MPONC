from helper import gdf_cache_filenames, graph_filenames, CACHE_DIR
from config import ID_LIST, PLOT_CITIES, CTY_KEY, RHO_L, ALPHA_L, T_MAX_L, NUM_AGENTS
from download_extract import download_and_extract_all
from gdf_handler import load_gdf, create_gdf
from graph_handler import load_graph, create_graph, save_graph
from amtdens_distances import compute_amts_dens, compute_centroid_distances
from simulation import run_simulation
from visualization import plot_city
from tqdm import tqdm
from pathlib import Path
import pickle
import numpy as np
import time

# =========================
# FOUR STEP MODEL FUNCTIONS
# =========================

def generate_trips(centroids):
    """ Estimate trip generation based on some criteria (e.g., population). """
    trip_counts = {}
    for (lon, lat, region_name, is_beltline, geoid) in centroids:
        # Placeholder logic for trip generation based on a simple factor
        trip_counts[geoid] = np.random.poisson(lam=100)  # Using a Poisson distribution as an example
    return trip_counts


def distribute_trips(trip_counts, centroids):
    """ Distribute trips using a gravity model or similar approach. """
    trip_distribution = {}
    total_trips = sum(trip_counts.values())

    # Placeholder logic for distributing trips
    for origin_geoid, trips in trip_counts.items():
        destination_counts = {}
        for (lon, lat, region_name, is_beltline, geoid) in centroids:
            # Placeholder logic for simple distribution based on distance
            destination_counts[geoid] = trips * np.random.random()  # Random distribution for demo
        trip_distribution[origin_geoid] = destination_counts
    return trip_distribution


def modal_split(trip_distribution):
    """ Perform a modal split on the trip distribution. """
    split_distribution = {}
    for origin, destinations in trip_distribution.items():
        split_distribution[origin] = {dest: trips * 0.7 for dest, trips in destinations.items()}  # 70% of trips by car
        split_distribution[origin].update(
            {dest: trips * 0.3 for dest, trips in destinations.items()})  # 30% by public transport
    return split_distribution


def route_assignment(split_distribution, g):
    """ Assign routes based on the network. """
    assigned_routes = {}
    for origin, destinations in split_distribution.items():
        for destination, trips in destinations.items():
            if trips > 0:
                # Placeholder for route assignment logic
                assigned_routes[(origin, destination)] = trips  # Direct assignment for demo
    return assigned_routes


def main():
    # ========================
    # DOWNLOAD AND EXTRACT ZIP
    # ========================
    simulation_start_time = time.time()
    
    shapefile_paths = download_and_extract_all()

    # =======================
    # GDF FILE INITIALIZATION
    # =======================

    # Load or create GeoDataFrame
    
    if all(Path(gdf_cache_filenames[i]).exists() for i in gdf_cache_filenames):
        combined_gdf = load_gdf(gdf_cache_filenames)
    else:
        combined_gdf = create_gdf(shapefile_paths, gdf_cache_filenames)

    # =========================
    # GRAPH FILE INITIALIZATION
    # =========================

    # Load or create Graph
    graph_file = graph_filenames[1]
    if Path(graph_file).exists():
        # Load existing graph and its IDs
        g, saved_IDS = load_graph(graph_file, combined_gdf)

        # Populate used_IDS based on current valid IDs in gdf_1
        used_IDS = [ID for ID, _ in ID_LIST if ID in set(combined_gdf['ID'])]
        
        # Compare saved_IDS with current IDs
        if set(saved_IDS) != set(used_IDS):
            print("\nRegions have changed. Recreating the graph...")
            g, used_IDS = create_graph(combined_gdf)
            save_graph(g, used_IDS, graph_file)
    else:
        # Create new graph
        g, used_IDS = create_graph(combined_gdf)
        save_graph(g, used_IDS, graph_file)

    # =========================
    # COMPUTE AMENITY DENSITIES
    # =========================

    amts_dens = None
    amts_dens = compute_amts_dens(combined_gdf, used_IDS)

    # ==========================
    # COMPUTE CENTROID DISTANCES
    # ==========================

    # Initialize centroids
    centroids = []
    # tuple format: (longitude, latitude, region_name, is_beltline, ID)

    ID_info = {ID: is_beltline for ID, is_beltline in ID_LIST if ID in used_IDS}

    # ================================
    # CENTROID INITIALIZATION FROM IDS
    # ================================
    for ID in tqdm(used_IDS[:-1], desc="\nInitializing Centroids", unit="centroid"):
        # Is_beltline
        is_beltline = ID_info.get(ID, False)

        # Fetch ID instance from combined_gdf
        gdf_sub = combined_gdf[combined_gdf['ID'] == ID]

        # Combined geometry of all geometries in gdf_sub
        combined_geometry = gdf_sub.geometry.union_all()

        # Initialize centroid with coordinates
        centroid = combined_geometry.centroid
        centroids.append((centroid.x, centroid.y, gdf_sub['Name'].iloc[0], is_beltline, ID))

    # Compute centroid distances
    centroid_distances = compute_centroid_distances(centroids, g, used_IDS)

    # ========================
    # RUN TRANSPORTATION MODEL
    # ========================

    # Step 1: Generate trips
    trip_counts = generate_trips(centroids)

    # Step 2: Distribute trips
    trip_distribution = distribute_trips(trip_counts, centroids)

    # Step 3: Modal Split
    split_distribution = modal_split(trip_distribution)

    # Step 4: Route Assignment
    assigned_routes = route_assignment(split_distribution, g)

    # ==============
    # RUN SIMULATION
    # ==============

    run_simulation(centroids, g, amts_dens, centroid_distances, assigned_routes, simulation_start_time)

    simulation_end_time = time.time()
    print(f"Completed simulation(s) after {simulation_end_time - simulation_start_time:.2f} seconds.\n")


    # =======================
    # PLOT SIMULATION RESULTS
    # =======================

    plot_start_time = time.time()
    
    if PLOT_CITIES:
        for rho in RHO_L:
            for alpha in ALPHA_L:
                for t_max in T_MAX_L:
                    pickle_filename = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{t_max}.pkl"
                    pickle_path = CACHE_DIR / pickle_filename
                    if pickle_path.exists():
                        with open(pickle_path, 'rb') as file:
                            city = pickle.load(file)
                        figkey = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{t_max}"
                        plot_city(city, g, combined_gdf, figkey=figkey)
                    else:
                        print(f"Pickle file '{pickle_filename}' does not exist. Skipping plotting.")
    
    plot_end_time = time.time()
    
    print(f"Completed plotting after {plot_end_time - plot_start_time:.2f} seconds.")


if __name__ == "__main__":
    main()
