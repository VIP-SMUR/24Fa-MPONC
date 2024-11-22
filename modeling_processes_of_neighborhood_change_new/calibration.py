# calibration.py

from config import CTY_KEY, NUM_AGENTS, T_MAX_RANGE
from helper import FIGURE_PKL_CACHE_DIR
import pickle


def calibrate(rho, alpha):
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
    simulated_income = df_data['Expected Income']
    expected_income = df_data['Avg Income']
    
    tot_difference = (expected_income - simulated_income).abs().sum()
    
    return figkey, tot_difference
    
    
        
        