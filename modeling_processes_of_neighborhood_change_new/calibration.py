# calibration.py

from config import CTY_KEY, NUM_AGENTS, T_MAX_RANGE, viewData
from helper import FIGURE_PKL_CACHE_DIR
import numpy as np
import pickle


def calibrate(rho, alpha, geo_id_to_income):
    """ Return the total difference between the simulated and expected incomes of each region """
    figkey = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{T_MAX_RANGE}"
    pickle_filename = f"{figkey}.pkl"
    pickle_path = FIGURE_PKL_CACHE_DIR / pickle_filename

    # Check existence
    if not pickle_path.exists():
        raise FileNotFoundError(f"Pickle file '{pickle_path}' does not exist.")

    # Access city object
    with open(pickle_path, 'rb') as file:
        city = pickle.load(file)

    # Fetch data
    df_data = city.get_data()
    df_data.set_index('Simulation_ID', inplace=True)
    
    # Remove GEO_ID's nonexistant in geo_id_to_income, keep relevant columns
    df_filtered = df_data.loc[geo_id_to_income.keys(), ['Avg Income', 'Expected Income']]
    
    # Remove rows where Expected income is NA
    df_filtered = df_filtered.dropna(subset=['Expected Income'])
    
    # Extract arrays of expected and simulated incomes
    simulated_income = df_filtered['Avg Income']
    expected_income = df_filtered['Expected Income']

    # Handle missing or invalid data (e.g., NaN values)
    simulated_income = simulated_income.dropna()
    expected_income = expected_income[simulated_income.index.isin(geo_id_to_income.keys())]

    if viewData:
        print(f"Number of rows in DataFrame: {df_filtered.shape[0]} after cleaning")
        print("First 5 rows of simulated_income:")
        print(simulated_income.head())
        print("First 5 rows of expected_income:")
        print(expected_income.head())

    # Calculate total absolute difference
    tot_difference = np.abs(expected_income - simulated_income).sum()

    return figkey, tot_difference

#NOTE: Regions with 0 population have simulated_income of 0
