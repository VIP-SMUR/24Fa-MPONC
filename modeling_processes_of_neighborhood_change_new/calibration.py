# calibration.py

from config import CTY_KEY, NUM_AGENTS, T_MAX_RANGE, viewData
from helper import FIGURE_PKL_CACHE_DIR
import numpy as np
import pickle


def calibrate(rho, alpha, geo_id_to_income):
    """ Return the total difference between the simulated and expected incomes of each region """
    # Fetch data for parameters 'rho', 'alpha', 't'
    figkey = f"{CTY_KEY}_{rho}_{alpha}_{NUM_AGENTS}_{T_MAX_RANGE}"
    pickle_filename = f"{figkey}.pkl"
    pickle_path = FIGURE_PKL_CACHE_DIR / pickle_filename
    # Check existence
    if not pickle_path.exists():
        raise FileNotFoundError(f"Pickle file '{pickle_path}' does not exist.")
    with open(pickle_path, 'rb') as file:
        city = pickle.load(file)
    # Fetch data
    df_data = city.get_data()
    
    df_data.set_index('Simulation_ID', inplace=True)
    
    #TODO: geo_id_to_income.keys() (the 'GEO_ID's from the census income data CSV's) DOES NOT MATCH the the indices of city.get_data ('Simulation_IDs' column from layer GDF's)
    # List of ID's that we have data for
    valid_ids = set(geo_id_to_income.keys())
    # # Filter df_data to include only valid_ids
    df_data = df_data[df_data.index.isin(valid_ids)]
    
    simulated_income = df_data['Avg Income']
    expected_income = np.array(list(geo_id_to_income.values()))
    
    print(f"Number of rows in DataFrame: {df_data.shape[0]}")

    print(simulated_income.head())
    print(simulated_income.dtypes)
    
    tot_difference = (expected_income - simulated_income).abs().sum()
    
    return figkey, tot_difference
    
    
        
        