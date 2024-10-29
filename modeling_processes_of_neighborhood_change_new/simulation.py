# simulation.py

from config import (RHO_L, ALPHA_L, T_MAX_L, TAU, NUM_AGENTS, RUN_EXPERIMENTS, CTY_KEY, DATA_DIR, FIGURES_DIR)
from Agent import Agent
from City import City
from itertools import product
from joblib import Parallel, delayed
import numpy as np
import pickle
import time

# ===============================
# SIMULATION EXECUTION LOGIC
# ===============================

# Run all simulations (parallel processing)
def run_simulation(centroids, g, amts_dens, centroid_distances, assigned_routes):
    if not RUN_EXPERIMENTS:
        return

    # Combination of all parameters
    simulation_params = list(product(RHO_L, ALPHA_L, T_MAX_L))
    
    # Total tasks
    total_tasks = len(simulation_params)
    
    # Number of CPU's
    n_jobs = -1 # maximum
    
    print("Simulating...")
    
    # Run parallel processing
    Parallel(n_jobs=n_jobs, backend='loky')(
        delayed(single_simulation)(
            rho, alpha, t_max, centroids, g, amts_dens, centroid_distances, assigned_routes
        )
        for rho, alpha, t_max in simulation_params
    )

    print("Completed simulation(s).\n")
        
# Single simulation run
def single_simulation(rho, alpha, t_max, centroids, g, amts_dens, centroid_distances, assigned_routes):
    np.random.seed(0)

    # Initialize city and agents
    city = City(centroids, g, amts_dens, centroid_distances, rho=rho)
    agt_dows = np.diff([1 - (1 - x) ** TAU for x in np.linspace(0, 1, NUM_AGENTS + 1)]) 
    agts = [Agent(i, dow, city, alpha=alpha) for i, dow in enumerate(agt_dows)]

    city.set_agts(agts)
    city.update()

    # Iterate through timesteps
    for t in range(t_max):
        for a in agts:
            # Find the trips assigned to this agent based on the assigned routes
            # This logic will need to be tailored based on how agents are supposed to interact with routes
            a.assign_routes(assigned_routes)  # Assuming there's a method to assign routes

        for a in agts:
            a.act()
        city.update()
        for a in agts:
            a.learn()
        
        if (t + 1) in T_MAX_L:
            for a in city.agts:
                a.avg_probabilities = a.tot_probabilities / (t + 1)

            # Pickle city object
            pickle_filename = f"{CTY_KEY}_{rho}_{alpha}_{t + 1}.pkl"
            start_time = time.time()
            with open(FIGURES_DIR / pickle_filename, 'wb') as file:
                pickle.dump(city, file, protocol=pickle.HIGHEST_PROTOCOL)
            end_time = time.time()
            
            print(f"Pickled {pickle_filename} in {end_time - start_time:.2f} seconds.")
            
            # ==================================
            # CENTROID DATA TO CSV via DATAFRAME
            # ==================================
            df_data = city.get_data()

            # CSV filename
            csv_filename = f"{CTY_KEY}_{rho}_{alpha}_{t + 1}_data.csv"
            
            # Save dataframe to CSV file
            csv_path = DATA_DIR / csv_filename
            df_data.to_csv(csv_path, index=False)
