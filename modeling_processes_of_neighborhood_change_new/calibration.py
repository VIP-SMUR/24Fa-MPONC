# calibration.py

from simulation import run_single_simulation_calibration
from config import CTY_KEY, NUM_AGENTS, T_MAX_RANGE, viewData
from helper import FIGURE_PKL_CACHE_DIR
from pymoo.core.problem import Problem
from pymoo.core.repair import Repair
from joblib import Parallel, delayed
import numpy as np
import pickle

class Calibration(Problem):
    def __init__(
        self, 
        geo_id_to_income,
        centroids,
        g,
        amts_dens,
        centroid_distances,
        assigned_routes,
        endowments,
        n_jobs=-1
        ):
        # n_var=2 [Rho, Alpha]
        # n_obj=1 # one objective: minimize income difference
        # xl and xu -> lower and upper bounds for each of the 2 variables
        super().__init__(
            n_var=2, 
            n_obj=1, 
            n_constr=0,
            xl=np.array([8, 0.1]),
            xu=np.array([32, 0.9])
            )
        
        self.geo_id_to_income = geo_id_to_income
        self.centroids = centroids
        self.g = g
        self.amts_dens = amts_dens
        self.centroid_distances = centroid_distances
        self.assigned_routes = assigned_routes
        self.endowments = endowments
        self.n_jobs = n_jobs

    def _evaluate(self, X, out, *args, **kwargs):
        # X is a 2D array of shape (population_size, 2)
        # We need to evaluate the objective for each row in X.
        
        results = Parallel(n_jobs=self.n_jobs)(
            delayed(self.get_error)(X[i, 0], X[i, 1], self.geo_id_to_income)
            for i in range(len(X))
        )
        
        tot_diffs = []
        
        for diff in results:
            tot_diffs.append(diff)
        
        out["F"] = np.array(tot_diffs).reshape(-1,1)
    
    def get_error(self, rho, alpha, geo_id_to_income):
        """ Return the total difference between the simulated and expected incomes of each region """
        figkey = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{T_MAX_RANGE}"
        pickle_path = FIGURE_PKL_CACHE_DIR / f"{figkey}.pkl"

        # Check existence
        if not pickle_path.exists():
            _ = run_single_simulation_calibration(
                    rho=rho,
                    alpha=alpha,
                    centroids=self.centroids,
                    g=self.g,
                    amts_dens=self.amts_dens,
                    centroid_distances=self.centroid_distances,
                    assigned_routes=self.assigned_routes,
                    endowments=self.endowments,
                    geo_id_to_income=self.geo_id_to_income
                )

        # Access city object
        with open(pickle_path, 'rb') as file:
            city = pickle.load(file)

        # Fetch data
        df_data = city.get_data()
        df_data.set_index('Simulation_ID', inplace=True)
        
        # Use only geoid's existing in geo_id_to_income, & keep relevant columns
        df_filtered = df_data.loc[geo_id_to_income.keys(), ['Avg Income', 'Expected Income']]
        
        # Remove rows where Expected income is NA
        df_filtered = df_filtered.dropna(subset=['Expected Income'])
        
        # Extract arrays of expected and simulated incomes
        simulated_income = df_filtered['Avg Income']
        expected_income = df_filtered['Expected Income']

        # Handle missing or invalid data (e.g., NaN values) in simulated_incomes
        simulated_income = simulated_income.dropna()

        if viewData:
            print(f"Number of rows in DataFrame: {df_filtered.shape[0]} after cleaning")
            print("First 5 rows of simulated_income:")
            print(simulated_income.head())
            print("First 5 rows of expected_income:")
            print(expected_income.head())

        # Calculate total absolute difference
        tot_difference = np.abs(expected_income - simulated_income).sum()

        return tot_difference

class MyRepair(Repair):
    """ Manually choose how to round Rho and Alpha parameters """

    def _do(self, problem, X, **kwargs):
        X[:, 0] = np.round(X[:, 0]).astype(int)     # Rho -> nearest integer
        X[:, 1] = np.round(X[:, 1], 2)  # Alpha -> hundredth place
        return X

#NOTE: Regions with 0 population have simulated_income of 0