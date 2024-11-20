# main.py

from collections import defaultdict

from helper import gdf_cache_filenames, GRAPH_FILE, GIFS_CACHE_DIR, FIGURES_DIR, T_MAX_L, SAVED_IDS_FILE
from config import PLOT_CITIES, RHO_L, ALPHA_L, AMENITY_TAGS, N_JOBS, GIF_NUM_PAUSE_FRAMES, GIF_FRAME_DURATION, ID_LIST
from file_download_manager import download_and_extract_layers_all
from economic_distribution import economic_distribution
from gdf_handler import load_gdf, create_gdf
from graph_handler import load_graph, create_graph, save_graph
from amt_densities import compute_amts_dens
from centroid_distances import cached_centroid_distances
from simulation import run_simulation
from visualization import plot_city
from gif import process_pdfs_to_gifs
from centroids import create_centroids
from saved_IDS import save_current_IDS, load_previous_IDS
from pathlib import Path
from itertools import product
from joblib import Parallel, delayed
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib

# =========================
# FOUR STEP MODEL FUNCTIONS
# =========================

def generate_trips(centroids, amts_dens, base_trips=100):
    """
    Estimate trip generation based on amenity scores.

    Parameters:
    centroids (list): List of (lon, lat, region_name, is_beltline, geoid)
    amts_dens (list): List of amenity scores for each zone
    base_trips (int): Base number of trips to scale by amenity scores

    Returns:
    dict: Dictionary mapping geoid to number of generated trips
    """
    trip_counts = {}
    # Normalize amenity scores to sum to 1 for use as probabilities
    total_amenity_score = sum(amts_dens)
    amenity_probabilities = [score / total_amenity_score for score in amts_dens]

    for idx, (lon, lat, region_name, is_beltline, geoid) in enumerate(centroids):
        # Generate trips based on amenity score probability
        trip_counts[geoid] = np.random.poisson(lam=base_trips * amenity_probabilities[idx])

    return trip_counts


def distribute_trips(trip_counts, centroids, amts_dens, centroid_distances):
    """
    Distribute trips using a gravity model based on amenity scores and transportation costs.

    Parameters:
    trip_counts (dict): Dictionary of trips generated from each origin zone
    centroids (list): List of centroid data (lon, lat, region_name, is_beltline, geoid)
    amts_dens (list): List of amenity scores for each zone
    centroid_distances (dict): Dictionary of distances between centroids

    Returns:
    dict: Nested dictionary with origin-destination trip counts
    """
    trip_distribution = {}

    # Create mapping from geoid to index for amenity scores
    geoid_to_index = {centroid[4]: idx for idx, centroid in enumerate(centroids)}

    for origin_geoid, origin_trips in trip_counts.items():
        origin_idx = geoid_to_index[origin_geoid]
        destination_counts = {}

        # Calculate denominator (sum of amenity * friction factors for all destinations)
        denominator = 0
        for dest_centroid in centroids:
            dest_geoid = dest_centroid[4]
            dest_idx = geoid_to_index[dest_geoid]

            # Get transportation cost (distance) between origin and destination
            try:
                distance = centroid_distances[origin_geoid, dest_geoid]
            except IndexError:
                distance = float('inf')

            # Use distance as friction factor F
            friction_factor = 1 / max(distance, 0.1)  # Avoid division by zero

            # Sum A_j * F_ij
            denominator += amts_dens[dest_idx] * friction_factor

        # Calculate trips to each destination
        for dest_centroid in centroids:
            dest_geoid = dest_centroid[4]
            dest_idx = geoid_to_index[dest_geoid]

            # Get transportation cost (distance) between origin and destination
            try:
                distance = centroid_distances[origin_geoid, dest_geoid]
            except IndexError:
                distance = float('inf')

            friction_factor = 1 / max(distance, 0.1)  # Avoid division by zero

            # Calculate T_ij using the formula:
            # T_ij = P_i * (A_j * F_ij) / Σ(A_j * F_ij)
            if denominator > 0:
                trips = origin_trips * (amts_dens[dest_idx] * friction_factor) / denominator
            else:
                trips = 0

            destination_counts[dest_geoid] = trips

        trip_distribution[origin_geoid] = destination_counts

    return trip_distribution


def modal_split(trip_distribution, car_ownership_rate=0.7):
    """
    Perform a modal split on the trip distribution.

    Parameters:
    trip_distribution (dict): Nested dictionary of trips between origins and destinations
    car_ownership_rate (float): Proportion of trips made by car (default 0.7)

    Returns:
    dict: Dictionary containing trips split by mode
    """
    modes = {
        'car': car_ownership_rate,
        'transit': 1 - car_ownership_rate
    }

    split_distribution = defaultdict(lambda: defaultdict(dict))
    for origin, destinations in trip_distribution.items():
        for dest, trips in destinations.items():
            for mode, rate in modes.items():
                split_distribution[origin][dest][mode] = trips * rate

    return split_distribution


def route_assignment(split_distribution, g):
    """
    Assign routes based on the network.

    Parameters:
    split_distribution (dict): Nested dictionary of trips split by mode
    g (networkx.Graph): Transportation network graph

    Returns:
    dict: Dictionary of assigned routes with volumes
    """
    assigned_routes = defaultdict(float)

    for origin in split_distribution:
        for destination in split_distribution[origin]:
            for mode, trips in split_distribution[origin][destination].items():
                if trips > 0:
                    # For now, just store the total volume between O-D pairs
                    # TODO: Implement actual route assignment using shortest paths
                    route_key = (origin, destination, mode)
                    assigned_routes[route_key] += trips

    return dict(assigned_routes)


def main():
    # ========================
    # DOWNLOAD AND EXTRACT ZIP
    # ========================

    shapefile_paths = download_and_extract_layers_all()
    
    endowments = economic_distribution()
    
    # =============================
    # CHECK IF REGIONS HAVE CHANGED
    # =============================
    regen_gdf_and_graph = True
    if Path(SAVED_IDS_FILE).exists():
        saved_IDS = load_previous_IDS(SAVED_IDS_FILE)
        if set(saved_IDS) == set(ID_LIST):
            regen_gdf_and_graph = False
    
    save_current_IDS(ID_LIST, SAVED_IDS_FILE)
    
    if regen_gdf_and_graph:
        print("Regions have changed. Creating new Geodataframe and OSMNX Graph.\n")
        
    # =======================
    # GDF FILE INITIALIZATION
    # =======================

    gdf_start_time = time.time()
    print("Processing Geodataframe(s)...")    
        
        
    # Create or load GDF
    if all(Path(gdf_cache_filenames[i]).exists() for i in gdf_cache_filenames):
        if regen_gdf_and_graph:
            print(f"Processing Geodataframe ...")  
            gdf = create_gdf(shapefile_paths, gdf_cache_filenames)
        else:
            gdf = load_gdf(gdf_cache_filenames)
    else:
        print(f"Processing Geodataframe ...")  
        gdf = create_gdf(shapefile_paths, gdf_cache_filenames)
        
    # Check if geometries are valid 
    if not gdf.is_valid.all():
        gdf['geometry'] = gdf['geometry'].buffer(0)
        if not gdf.is_valid.all():
            raise ValueError("Some geometries are invalid.")

    #FIXME [Debugging purposes]: view graph of geodataframe:
    # matplotlib.use('TkAgg')
    # gdf.plot()
    # plt.show()
    # matplotlib.use('Agg')

    gdf_end_time = time.time()
    print(f"GeoDataFrame generation complete after {gdf_end_time - gdf_start_time:.2f} seconds\n")

    # =========================
    # GRAPH FILE INITIALIZATION
    # =========================

    graph_start_time = time.time()
    print("Generating graph from OSMnx...")

    if Path(GRAPH_FILE).exists():
        if regen_gdf_and_graph:
            g = create_graph(gdf)
            save_graph(g, GRAPH_FILE)
        else:
            g = load_graph(GRAPH_FILE)
            print(f"Loaded existing graph from {GRAPH_FILE}")
    else:
        g = create_graph(gdf)
        save_graph(g, GRAPH_FILE)

    graph_end_time = time.time()
    print(f"Graph generation complete after {graph_end_time - graph_start_time:.2f} seconds\n")

    # ================================
    # CENTROID INITIALIZATION FROM IDS
    # ================================
    centroid_start_time = time.time()
    print("Initializing centroids...")

    centroids = create_centroids(gdf)

    centroid_end_time = time.time()
    print(f"Centroid initialization completed after {centroid_end_time - centroid_start_time:.2f} seconds\n")

    # =========================
    # COMPUTE AMENITY DENSITIES
    # =========================
    amts_dens_start_time = time.time()
    print("Processing amenities...")

    amts_dens = compute_amts_dens(gdf, AMENITY_TAGS)

    amts_dens_end_time = time.time()
    print(f"Completed amenity density calculations after {amts_dens_end_time - amts_dens_start_time:.2f} seconds\n")

    # ==========================
    # COMPUTE CENTROID DISTANCES
    # ==========================
    distances_start_time = time.time()
    print("Processing centroid distances...")

    centroid_distances = cached_centroid_distances(centroids, g)

    distances_end_time = time.time()
    print(f"Completed distance calculations after {distances_end_time - distances_start_time:.2f} seconds\n")

    # ========================
    # RUN TRANSPORTATION MODEL
    # ========================
    transport_start_time = time.time()
    print("Running transportation model...")

    # Step 1: Generate trips
    trip_counts = generate_trips(centroids, amts_dens, base_trips=100)

    # Step 2: Distribute trips using gravity model
    trip_distribution = distribute_trips(trip_counts, centroids, amts_dens, centroid_distances)

    # Step 3: Modal Split with 70% car ownership rate
    split_distribution = modal_split(trip_distribution, car_ownership_rate=0.7)

    # Step 4: Route Assignment
    assigned_routes = route_assignment(split_distribution, g)

    transport_end_time = time.time()
    print(f"Completed transportation model after {transport_end_time - transport_start_time:.2f} seconds\n")

    # ==============
    # RUN SIMULATION
    # ==============
    simulation_start_time = time.time()
    print("Simulating...")

    run_simulation(centroids, g, amts_dens, centroid_distances, assigned_routes, endowments)

    simulation_end_time = time.time()
    print(f"Completed simulation(s) after {simulation_end_time - simulation_start_time:.2f} seconds.\n")

    # ==============================
    # VISUALIZATION LOGIC (PLOTTING)
    # ==============================
    if PLOT_CITIES:
        plot_start_time = time.time()
        print("Plotting...")

        simulation_params = list(product(RHO_L, ALPHA_L, T_MAX_L))

        Parallel(n_jobs=N_JOBS, backend='loky')(
            delayed(plot_city)(
                rho, alpha, t_max, centroids, g, gdf
            )
            for rho, alpha, t_max in simulation_params
        )

        plot_end_time = time.time()
        print(f"Completed plotting after {plot_end_time - plot_start_time:.2f} seconds.")

        # ======================
        # CREATE SIMULATION GIFS
        # ======================
        gif_start_time = time.time()
        print("Creating GIF(s)...")

        process_pdfs_to_gifs(FIGURES_DIR, GIFS_CACHE_DIR, duration=GIF_FRAME_DURATION, num_pause_frames=GIF_NUM_PAUSE_FRAMES)

        gif_end_time = time.time()
        print(f"Completed creating GIF's after {gif_end_time - gif_start_time:.2f} seconds.")


if __name__ == "__main__":
    main()

#TO-DO list:
#TODO: Transition to census tracts [DONE]
#TODO: Replace Lorentz curve with actual distribution (2010) [DONE]
#TODO: Initialize "is_beltline" using Carlos's script
#TODO: Query from past OSMNX (talk to atharva, PEI)

#TODO: Address funky data in Income/Population CSV's
#TODO: Address "graph is not strongly connected"
        
#TODO: make random, make thresholds for car ownership, integrate demographic data with prices.
#TODO: Separate 4-step-model into its own .py file

""" Spring 2025 TODO's: """
#TODO: check if gif already exists before creating (cached)
#TODO: centroid distance = avg of: shortest paths between every node in a region A to every node in region B
#TODO: Add weights to amenities for amenity score calculation

""" Quality of Life: """
#TODO: cache individual centroid distances
#TODO: make GIF speed dynamic based on configuration