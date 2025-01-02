# main.py

from collections import defaultdict
from helper import gdf_cache_filenames, GRAPH_FILE, GIFS_CACHE_DIR, FIGURES_DIR, T_MAX_L, SAVED_IDS_FILE
from config import RUN_CALIBRATION, CTY_KEY, NUM_AGENTS, T_MAX_RANGE, PLOT_CITIES, RHO_L, ALPHA_L, AMENITY_TAGS, N_JOBS, GIF_NUM_PAUSE_FRAMES, GIF_FRAME_DURATION, ID_LIST, RELATION_IDS, viewData
from file_download_manager import download_and_extract_layers_all
from economic_distribution import economic_distribution
from gdf_handler import load_gdf, create_gdf, print_overlaps
from graph_handler import load_graph, create_graph, save_graph
from amtdens_distances import compute_amts_dens
from centroid_distances import cached_centroid_distances
from simulation import run_simulation
from visualization import plot_city
from gif import process_pdfs_to_gifs
from centroids import create_centroids
from save_IDS import save_current_IDS, load_previous_IDS
from calibration import Calibration, MyRepair
from in_beltline import fetch_beltline_nodes
from pathlib import Path
from itertools import product
from joblib import Parallel, delayed
from four_step_model import run_four_step_model
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination import get_termination
from pymoo.optimize import minimize
import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import matplotlib

OVERALL_START_TIME = time.time()

def main():
    # ========================
    # DOWNLOAD AND EXTRACT ZIP
    # ========================

    print("Processing Shapefiles and Census data...")
    file_start_time = time.time()    

    shapefile_paths = download_and_extract_layers_all()
    
    endowments, geo_id_to_income = economic_distribution()
    
    n = ((len(geo_id_to_income)))
    print(f"\nNumber of tracts used to calculate endowment distribution: {n}\n")
    
    file_end_time = time.time()
    
    print(f"File download and extraction complete after {file_end_time - file_start_time:.2f} seconds.\n")
    
    
    # =============================
    # CHECK IF REGIONS HAVE CHANGED
    # =============================
    regen_gdf_and_graph = False # Toggles True if counties have changed
    
    if Path(SAVED_IDS_FILE).exists():
        saved_IDS = load_previous_IDS(SAVED_IDS_FILE)
        if not set(saved_IDS) == set(ID_LIST):
            regen_gdf_and_graph = True
    
    save_current_IDS(ID_LIST, SAVED_IDS_FILE)
    
    if regen_gdf_and_graph:
        print("Regions have changed. Saving ID's and recreating Geodataframe and Graph.\n")
        
    # =======================
    # GDF FILE INITIALIZATION
    # =======================

    gdf_start_time = time.time()
    print("Processing Geodataframe(s)...")    
    
    beltline_geom = fetch_beltline_nodes(RELATION_IDS)
    if beltline_geom is None:
        print("Failed to fetch BeltLine geometries.")
        
    # Create or load GDF
    if all(Path(gdf_cache_filenames[i]).exists() for i in gdf_cache_filenames):
        if regen_gdf_and_graph:
            gdf, num_geometries, num_geometries_individual = create_gdf(shapefile_paths, gdf_cache_filenames, beltline_geom)
        else:
            gdf, num_geometries, num_geometries_individual = load_gdf(gdf_cache_filenames, beltline_geom)
    else:
        gdf, num_geometries, num_geometries_individual = create_gdf(shapefile_paths, gdf_cache_filenames, beltline_geom)
        
    print(f"GDF contains {num_geometries} regions")
    for i in range(len(num_geometries_individual)):
        print(f"Region {i+1} contains {num_geometries_individual[i]} geometries.")
        
    # Check if geometries are valid 
    if not gdf.is_valid.all():
        gdf['geometry'] = gdf['geometry'].buffer(0)
        if not gdf.is_valid.all():
            raise ValueError("Some geometries are invalid.")
    
    if viewData:
        print(gdf.columns)

    """ CHECK OVERLAPS """
    print_overlaps(gdf)
    
    # [VIEW GRAPH]
    # *freezes code - re-run simulation with this commented out to proceed*
    
    # matplotlib.use('TkAgg')
    # gdf.plot()
    # plt.show()
    # matplotlib.use('Agg')

    gdf_end_time = time.time()
    print(f"GeoDataFrame generation complete after {gdf_end_time - gdf_start_time:.2f} seconds.\n")

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
            print(f"Loaded existing graph from {GRAPH_FILE}.")
    else:
        g = create_graph(gdf)
        save_graph(g, GRAPH_FILE)

    graph_end_time = time.time()
    print(f"Graph generation complete after {graph_end_time - graph_start_time:.2f} seconds.\n")

    # ================================
    # CENTROID INITIALIZATION FROM IDS
    # ================================
    centroid_start_time = time.time()
    print("Initializing centroids...")

    centroids = create_centroids(gdf)

    centroid_end_time = time.time()
    print(f"Centroid initialization completed after {centroid_end_time - centroid_start_time:.2f} seconds.\n")

    # =========================
    # COMPUTE AMENITY DENSITIES
    # =========================
    amts_dens_start_time = time.time()
    print("Processing amenities...")

    amts_dens = compute_amts_dens(gdf, AMENITY_TAGS)

    amts_dens_end_time = time.time()
    print(f"Completed amenity density initialization after {amts_dens_end_time - amts_dens_start_time:.2f} seconds.\n")

    # ==========================
    # COMPUTE CENTROID DISTANCES
    # ==========================
    distances_start_time = time.time()
    print("Processing centroid distances...")

    centroid_distances = cached_centroid_distances(centroids, g)

    distances_end_time = time.time()
    print(f"Completed distance initialization after {distances_end_time - distances_start_time:.2f} seconds.\n")

    # ========================
    # RUN TRANSPORTATION MODEL
    # ========================
    transport_start_time = time.time()
    print("Running transportation model...")

    trip_counts, trip_distribution, split_distribution, assigned_routes = run_four_step_model(
        centroids=centroids,
        g=g,
        amts_dens=amts_dens,
        centroid_distances=centroid_distances,
        base_trips=100,
        car_ownership_rate=0.7
    )

    transport_end_time = time.time()
    print(f"Completed transportation model after {transport_end_time - transport_start_time:.2f} seconds.\n")

    # ==============
    # RUN SIMULATION
    # ==============
    simulation_start_time = time.time()
    print("Simulating...")

    run_simulation(centroids, g, amts_dens, centroid_distances, assigned_routes, endowments, geo_id_to_income)

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
                rho, alpha, t_max, centroids, beltline_geom
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

    # =============================================================
    # ACQUIRE CALIBRATION METRIC (EXPECTED MINUS SIMULATED INCOMES)
    # =============================================================
    if RUN_CALIBRATION:
        calibration_start_time = time.time()
        print("Running calibration...")
        problem = Calibration(
            geo_id_to_income,
            centroids,
            g,
            amts_dens,
            centroid_distances,
            assigned_routes,
            endowments,
        )
        algorithm = GA(
            pop_size=50,  # Number of parameter combinations to test
            repair=MyRepair(),
            eliminate_duplicates=True
        )

        termination = get_termination("n_gen", 30)  # Terminates after 30 generations

        results = minimize(
            problem,
            algorithm,
            termination,
            seed=1,
            save_history=True,
            verbose=True
        )
        
        X = results.X

        # If one-dimensional, handle shape
        if X.ndim == 1:
            X = X.reshape(1, -1)
            
        all_solutions = []
        # Loop over each generation in the history
        for gen, res in enumerate(results.history):
            # Population at this generation
            pop_X = res.pop.get("X")  # shape: (pop_size, n_var)
            pop_F = res.pop.get("F")  # shape: (pop_size, n_obj)

            for i in range(len(pop_X)):
                rho_val = pop_X[i, 0]
                alpha_val = pop_X[i, 1]
                tot_diff_val = pop_F[i, 0]  # objective is 1D, shape (pop_size,1)

                # Construct a figkey as you did before (adjust as needed)
                figkey = f"{CTY_KEY}_{int(rho_val)}_{alpha_val:.2f}_{NUM_AGENTS}_{T_MAX_RANGE}"

                # Append each row to a list
                all_solutions.append({
                    "figkey": figkey,
                    "rho": rho_val,
                    "alpha": alpha_val,
                    "tot_difference": tot_diff_val
                })    
                
        df_all = pd.DataFrame(all_solutions)
        df_all.to_csv(Path("data") / "optimization_results_all.csv", index=False)            
                
        # Print the Dataframe
        print("\nCalibration dataframe:") #TODO: remove later, visible just for debugging
        print(df_all)
                
        best_idx = df_all["tot_difference"].idxmin()
        best_params = df_all.loc[best_idx]

        best_rho = best_params["rho"]
        best_alpha = best_params["alpha"]
        best_diff = best_params["tot_difference"]
        print("\nBest parameters:")
        print(f"Rho: {best_rho}, Alpha: {best_alpha}")
        print(f"Income difference: {best_diff}")        

        calibration_end_time = time.time()
        print(f"Completed parameter calibration after {calibration_end_time - calibration_start_time:.2f} seconds.")
        
        
    OVERALL_END_TIME = time.time()
    print(f"\n[EVERYTHING DONE AFTER {OVERALL_END_TIME - OVERALL_START_TIME:.2f}s]")

if __name__ == "__main__":
    main()

#TO-DO list:
""" Functionality """
#TODO: Acquire optimal set of parameters to match 2010 data
#TODO: For 2010 calibration, query amenities from 2010
#TODO: Investigate funky amenity counts [!!]
#TODO: open economic/population links before attempting download
#TODO: add epsilon as a changeable parameter (check functionality in simulation)

#TODO: Investigate "not strongly connected graph"
    # No difference between graphs when extracting strongly connected component vs. not

""" Enhancement """
#TODO: Add weights to amenity types
#TODO: Change centroid distance to be avg of: shortest paths between every node in a region A to every node in region B
#TODO: Beltline attribute -  Beltline attribute: 1 if less than 1km, until 5 km decreases linearly to 0

""" Optimization """
#TODO: In calibration CSV, order parameters from least to greatest
#TODO: check if gif already exists before re-creating it
#TODO: Make amenity queries faster [!!!]
#TODO: Address approach of: loading GDF and GRAPH from cache for every simulation iteration, instead of passing as parameter
#TODO: Address: Creating 'Beltline' column every time a graph is generated [gdf_handler]
#TODO: cache individual centroid distances [?]

# Devam:
#TODO: make random, make thresholds for car ownership, integrate demographic data with prices.