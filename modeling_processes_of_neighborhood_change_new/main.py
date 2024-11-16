from helper import gdf_cache_filenames, graph_file, GIFS_DIR, FIGURES_DIR, T_MAX_L, used_IDS
from config import ID_LIST, PLOT_CITIES, RHO_L, ALPHA_L, AMENITY_TAGS, N_JOBS, GIF_NUM_PAUSE_FRAMES, GIF_FRAME_DURATION
from download_extract import download_and_extract_all
from gdf_handler import load_gdf, create_gdf
from graph_handler import load_graph, create_graph, save_graph
from amtdens_distances import compute_amts_dens, cached_centroid_distances
from simulation import run_simulation
from visualization import plot_city
from gif import process_pdfs_to_gifs
from centroids import create_centroids
from pathlib import Path
from itertools import product
from joblib import Parallel, delayed
import numpy as np
import time

# =========================
# FOUR STEP MODEL FUNCTIONS
# =========================

def generate_trips(centroids, amts_dens):
    """ Estimate trip generation based on some criteria (e.g., population). """
    trip_counts = {}
    # Normalize amenity scores to sum to 1 for use as probabilities
    total_amenity_score = sum(amts_dens)
    amenity_probabilities = [score / total_amenity_score for score in amts_dens]

    for idx, (lon, lat, region_name, is_beltline, geoid) in enumerate(centroids):
        # Use each centroid's amenity score as a probability factor for generating trips
        trip_counts[geoid] = np.random.poisson(lam=100 * amenity_probabilities[idx])

    return trip_counts

#TODO: make random, make thresholds for car ownership, integrate demographic data with prices.
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
    
    shapefile_paths = download_and_extract_all()

    # =======================
    # GDF FILE INITIALIZATION
    # =======================
    
    # Load or create GeoDataFrame
    
    if all(Path(gdf_cache_filenames[i]).exists() for i in gdf_cache_filenames):
        gdf = load_gdf(gdf_cache_filenames)
    else:
        gdf = create_gdf(shapefile_paths, gdf_cache_filenames)

    # =========================
    # GRAPH FILE INITIALIZATION
    # =========================
    
    graph_start_time = time.time()
    
    # Load or create Graph
    if Path(graph_file).exists(): 
        # PULL GRAPH FROM CACHE
        g, saved_IDS = load_graph(graph_file)
        
        # Compare saved_IDS with current IDs
        if set(saved_IDS) != set(used_IDS): # If different, create new graph
            print("Regions have changed. Recreating the graph...")
            g = create_graph(gdf)
            save_graph(g, used_IDS, graph_file)
    else: 
        # CREATE NEW GRAPH
        g = create_graph(gdf)
        save_graph(g, used_IDS, graph_file)
        
    graph_end_time = time.time()    
    print(f"New graph generated after {graph_end_time - graph_start_time:.2f} seconds\n")
    
    # ================================
    # CENTROID INITIALIZATION FROM IDS
    # ================================
    centroid_start_time = time.time()
    print("Initializing centroids...")
    
    centroids = create_centroids(gdf, ID_LIST)
        
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
    print("Processing distances...")
    
    centroid_distances = cached_centroid_distances(centroids, g)
    
    distances_end_time = time.time()
    print(f"Completed distance calculations after {distances_end_time - distances_start_time:.2f} seconds\n")

    # ========================
    # RUN TRANSPORTATION MODEL
    # ========================

    # Step 1: Generate trips
    trip_counts = generate_trips(centroids, amts_dens)

    # Step 2: Distribute trips
    trip_distribution = distribute_trips(trip_counts, centroids)

    # Step 3: Modal Split
    split_distribution = modal_split(trip_distribution)

    # Step 4: Route Assignment
    assigned_routes = route_assignment(split_distribution, g)

    # ==============
    # RUN SIMULATION
    # ==============
    simulation_start_time = time.time()
    print("Simulating...")
    
    run_simulation(centroids, g, amts_dens, centroid_distances, assigned_routes)

    simulation_end_time = time.time()
    print(f"Completed simulation(s) after {simulation_end_time - simulation_start_time:.2f} seconds.\n")

    # =======================
    # PLOT SIMULATION RESULTS
    # =======================
    if PLOT_CITIES:
        plot_start_time = time.time()
        print("Plotting...")
        
        # All combinations of parameters
        simulation_params = list(product(RHO_L, ALPHA_L, T_MAX_L))
        
        # Multiprocessing
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
    if PLOT_CITIES:
        gif_start_time = time.time()
        print("Creating GIF(s)...")
    
        process_pdfs_to_gifs(FIGURES_DIR, GIFS_DIR, duration=GIF_FRAME_DURATION, num_pause_frames=GIF_NUM_PAUSE_FRAMES)
        
        gif_end_time = time.time()
        print(f"Completed creating GIF's after {gif_end_time - gif_start_time:.2f} seconds.")


if __name__ == "__main__":
    main()

#TODO: make random, make thresholds for car ownership, integrate demographic data with prices.

#TODO: low priority: centroid distance = avg shortest path between every node in a region 
#TODO: only use regions in fulton and other county
    # Fetch all geometries within Fulton and Dekalb
    # Initialize list in config including regions tomark "BELTLINE"
        # Automatically assign "BELTLINE" to region ID's titled "BELTLINE0X"