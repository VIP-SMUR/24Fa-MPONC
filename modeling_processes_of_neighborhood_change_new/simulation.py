# simulation.py

from config import RHO_L, ALPHA_L, NUM_AGENTS, RUN_EXPERIMENTS, CTY_KEY, N_JOBS
from helper import DATA_DIR, FIGURE_PKL_CACHE_DIR, T_MAX_L
from Agent import Agent
from City import City
from itertools import product
from joblib import Parallel, delayed
import numpy as np
import pickle
import time

class SimulationManager:
    """Manages the execution of multiple simulation runs"""

    def __init__(self, centroids, g, amts_dens, centroid_distances):
        self.centroids = centroids
        self.g = g
        self.amts_dens = amts_dens
        self.centroid_distances = centroid_distances
        self.simulation_params = list(product(RHO_L, ALPHA_L))
        self.t_max = max(T_MAX_L)
        self.benchmarks = sorted(T_MAX_L)

    def initialize_agents(self, city, alpha, endowments):
        """Step 1: Initialize agents with sampling distribution"""
        # Generate agent endowments using economic_distribution.py
        agt_dows = endowments

        # Create agents with initial sampling distributions
        agents = [Agent(i, dow, city, alpha=alpha) for i, dow in enumerate(agt_dows)]
        return agents

    def run_parallel_simulations(self, assigned_routes, endowments):
        """Execute multiple simulations in parallel"""
        if not RUN_EXPERIMENTS:
            return

        # Run parallel processing using all available CPUs
        Parallel(n_jobs=N_JOBS, backend='loky')(
            delayed(self.run_single_simulation)(
                rho, alpha, assigned_routes, endowments
            )
            for rho, alpha in self.simulation_params
        )

    def run_single_simulation(self, rho, alpha, assigned_routes, endowments):
        """Execute a single simulation with given parameters"""
        start_time = time.time()
        
        # Set random seed based on parameters for reproducibility
        seed = int(rho * 1000 + alpha * 100)
        np.random.seed(seed)

        # Step 1: Initialize city and agents
        city = City(self.centroids, self.g, self.amts_dens, self.centroid_distances, rho=rho)
        agents = self.initialize_agents(city, alpha, endowments)
        city.set_agts(agents)
        city.update()

        # Track current benchmark for saving data
        benchmark_index = 0

        # Main simulation loop
        for t in range(self.t_max):
            self.execute_simulation_step(city, assigned_routes)

            # Save results at benchmark timesteps
            if (t + 1) == self.benchmarks[benchmark_index]:
                self.save_simulation_state(city, rho, alpha, t + 1)
                benchmark_index += 1
        
        # Log completion
        simulation_name = f"{rho}_{alpha}_{NUM_AGENTS}_{self.benchmarks[benchmark_index-1]}"
        end_time = time.time()
        print(f"Simulation {simulation_name} done [{end_time - start_time:.2f} s]")

    def execute_simulation_step(self, city, assigned_routes):
        """Execute one step of the simulation"""
        # Step 2: Modify routes and positions
        for agent in city.agts:
            agent.assign_routes(assigned_routes)

        # Step 3: Update positions and calculate costs
        for agent in city.agts:
            agent.act()
        city.update()
        for agent in city.agts:
            agent.learn()

    def save_simulation_state(self, city, rho, alpha, timestep):
        """Save simulation results to files"""
        # Update average probabilities for each agent
        for agent in city.agts:
            agent.avg_probabilities = agent.tot_probabilities / timestep

        # Save city state
        self._save_pickle(city, rho, alpha, timestep)

        # Save centroid data
        self._save_csv(city, rho, alpha, timestep)

    def _save_pickle(self, city, rho, alpha, timestep):
        """Save city state to pickle file"""
        pickle_filename = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{timestep}.pkl"
        with open(FIGURE_PKL_CACHE_DIR / pickle_filename, 'wb') as file:
            pickle.dump(city, file, protocol=pickle.HIGHEST_PROTOCOL)

    def _save_csv(self, city, rho, alpha, timestep):
        """Save centroid data to CSV"""
        df_data = city.get_data()
        csv_filename = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{timestep}_data.csv"
        csv_path = DATA_DIR / csv_filename
        df_data.to_csv(csv_path, index=False)


def run_simulation(centroids, g, amts_dens, centroid_distances, assigned_routes, endowments):
    """Main entry point for running simulations"""
    manager = SimulationManager(centroids, g, amts_dens, centroid_distances)
    manager.run_parallel_simulations(assigned_routes, endowments)