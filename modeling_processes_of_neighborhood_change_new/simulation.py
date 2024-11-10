# simulation.py

from config import (RHO_L, ALPHA_L, T_MAX_L, NUM_AGENTS, RUN_EXPERIMENTS, CTY_KEY)
from helper import TAU, DATA_DIR, CACHE_DIR
from Agent import Agent
from City import City
from itertools import product
from joblib import Parallel, delayed
import numpy as np
import pickle
import time

# ==========================
# SIMULATION EXECUTION LOGIC
# ==========================

# [ALL SIMULATIONS] (parallel processing)
def run_simulation(centroids, g, amts_dens, centroid_distances, assigned_routes, start_time):
    if not RUN_EXPERIMENTS:
        return

    # Combination of all parameters
    simulation_params = list(product(RHO_L, ALPHA_L))
    t_max = max(T_MAX_L)
    
    # Number of CPU's
    n_jobs = -1 # maximum
    
    print("\nSimulating...")
    
    # Run parallel processing
    Parallel(n_jobs=n_jobs, backend='loky')(
        delayed(single_simulation)(
            rho, alpha, t_max, centroids, g, amts_dens, centroid_distances, assigned_routes, start_time
        )
        for rho, alpha in simulation_params
    )
        
# [SINGLE SIMULATION]
def single_simulation(rho, alpha, t_max, centroids, g, amts_dens, centroid_distances, assigned_routes, start_time):
    seed = int(rho*1000 + alpha*100)
    np.random.seed(seed)

    # Initialize city
    city = City(centroids, g, amts_dens, centroid_distances, rho=rho)
    agt_dows = np.diff([1 - (1 - x) ** TAU for x in np.linspace(0, 1, NUM_AGENTS + 1)]) 
    
    # Initialize clean slate of agents based on Lorentz curve
    agts = [Agent(i, dow, city, alpha=alpha) for i, dow in enumerate(agt_dows)]

    city.set_agts(agts)
    city.update()
    
    # Timesteps at which to save data (T_MAX_L)
    benchmarks = sorted(T_MAX_L)
    benchmark_index = 0

    # Iterate through timesteps
    for t in range(t_max):
        
        for a in city.agts:
            # Find the trips assigned to this agent based on the assigned routes
            # This logic will need to be tailored based on how agents are supposed to interact with routes
            a.assign_routes(assigned_routes)  # Assuming there's a method to assign routes

        for a in city.agts:
            a.act()
        city.update()
        for a in city.agts: 
            a.learn()
        
    # After simulation completes, save results
        if (t + 1) == benchmarks[benchmark_index]:
            for a in city.agts:
                a.avg_probabilities = a.tot_probabilities / (t + 1)

            # Pickle city object
            pickle_filename = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{t + 1}.pkl"
            with open(CACHE_DIR / pickle_filename, 'wb') as file:
                pickle.dump(city, file, protocol=pickle.HIGHEST_PROTOCOL)
            
            # ==================================
            # CENTROID DATA TO CSV via DATAFRAME
            # ==================================
            df_data = city.get_data()

            # CSV filename
            csv_filename = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{t + 1}_data.csv"
            
            # Save dataframe to CSV file
            csv_path = DATA_DIR / csv_filename
            df_data.to_csv(csv_path, index=False)
            
            simulation_name = f"{rho}_{alpha}_{NUM_AGENTS}_{t + 1}"
            end_time = time.time()
            print(f"Simulation {simulation_name} done [{end_time - start_time:.2f} s]")
            
            benchmark_index += 1