# simulation.py

import numpy as np
import itertools
from tqdm import tqdm
import pickle
from config import (RHO_L, ALPHA_L, T_MAX_L, TAU, NUM_AGENTS, RUN_EXPERIMENTS, SAVE_DATA, CTY_KEY, DATA_DIR, FIGURES_DIR)
from Agent import Agent
from City import City

# ===============================
# SIMULATION EXECUTION LOGIC
# ===============================

def run_simulation(centroids, g, amts_dens, centroid_distances):
    if not RUN_EXPERIMENTS:
        return

    # Number of rho/alpha combinations
    rho_alpha_iterations = len(RHO_L) * len(ALPHA_L) * max(T_MAX_L)
    
    # Iterate
    with tqdm(total=rho_alpha_iterations, desc='Simulating:', unit='step') as pbar:
        for rho, alpha in itertools.product(RHO_L, ALPHA_L):
            # Ensure reproducibility 
            np.random.seed(0)

            # Initialize city and agents
            city = City(centroids, g, amts_dens, centroid_distances, rho=rho)
            agt_dows = np.diff([1 - (1 - x) ** TAU for x in np.linspace(0, 1, NUM_AGENTS + 1)]) 
            agts = [Agent(i, dow, city, alpha=alpha) for i, dow in enumerate(agt_dows)]

            city.set_agts(agts)
            city.update()

            # Iterate through t_max_l
            for t in range(max(T_MAX_L)):
                pbar.set_postfix(rho=rho, alpha=alpha, timestep=t)
                for a in agts:
                    a.act()
                city.update()
                for a in agts:
                    a.learn()
                    
                pbar.update(1)
                
                if (t + 1) in T_MAX_L:
                    for a in city.agts:
                        a.avg_probabilities = a.tot_probabilities / (t + 1)

                    # Pickle city object
                    pickle_filename = f"{CTY_KEY}_{rho}_{alpha}_{t + 1}.pkl"
                    with open(FIGURES_DIR / pickle_filename, 'wb') as file:
                        pickle.dump(city, file)
                    
                    # ==================================
                    # CENTROID DATA TO CSV via DATAFRAME
                    # ==================================
                    if SAVE_DATA:
                        df_data = city.get_data()

                        # CSV filename
                        csv_filename = f"{CTY_KEY}_{rho}_{alpha}_{t + 1}_data.csv"
                        
                        # Save dataframe to CSV file
                        csv_path = DATA_DIR / csv_filename
                        df_data.to_csv(csv_path, index=False)
