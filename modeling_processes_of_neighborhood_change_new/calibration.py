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

    # Ensure that only valid IDs are considered
    valid_ids = set(geo_id_to_income.keys())
    df_data = df_data[df_data.index.isin(valid_ids)]

    # Ensure `geo_id_to_income` is filtered and aligned with `df_data`
    filtered_geo_id_to_income = {id_: geo_id_to_income[id_] for id_ in df_data.index if id_ in geo_id_to_income}

    # Extract and align expected and simulated incomes
    simulated_income = df_data.loc[filtered_geo_id_to_income.keys(), 'Avg Income']
    expected_income = np.array(list(filtered_geo_id_to_income.values()))

    # Handle missing or invalid data (e.g., NaN values)
    simulated_income = simulated_income.dropna()
    expected_income = expected_income[simulated_income.index.isin(filtered_geo_id_to_income.keys())]

    print(f"Number of rows in DataFrame: {df_data.shape[0]}")
    print(simulated_income.head())
    print(simulated_income.dtypes)

    # Calculate total absolute difference
    tot_difference = np.abs(expected_income - simulated_income).sum()

    return figkey, tot_difference
