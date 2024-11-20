# endowment_distribution.py

import numpy as np
from config import NUM_AGENTS, ECONOMIC_URL, ECONOMIC_DATA_SKIP_ROWS, ECONOMIC_DATA_COL, POPULATION_URL, POPULATION_DATA_COL,  POPULATION_DATA_SKIP_ROWS
from file_download_manager import download_and_extract_census_data
import pandas as pd

incomes = np.array([])

def economic_distribution():
    # [INCOME]
    income_data = download_and_extract_census_data(ECONOMIC_URL, 'economic_data.zip', 'economic_data')
    income_df = pd.read_csv(income_data, skiprows=ECONOMIC_DATA_SKIP_ROWS, header=0)
    # [POPULATION]
    population_data = download_and_extract_census_data(POPULATION_URL, 'population_data.zip', 'population_data')
    population_df = pd.read_csv(population_data, skiprows=POPULATION_DATA_SKIP_ROWS, header=0)
    
    # [MARK INVALID ENTRIES WITH NaN]
    income_df[ECONOMIC_DATA_COL] = pd.to_numeric(income_df[ECONOMIC_DATA_COL], errors='coerce')
    population_df[POPULATION_DATA_COL] = pd.to_numeric(population_df[POPULATION_DATA_COL], errors='coerce')
    
    # [REMOVE UNCOMMON TRACTS; DROP NaN]
    merged_df = pd.merge(income_df[['GEO_ID', ECONOMIC_DATA_COL]], population_df[['GEO_ID', POPULATION_DATA_COL]], on='GEO_ID', how='inner')
    merged_df = merged_df.dropna(subset=[ECONOMIC_DATA_COL, POPULATION_DATA_COL])
    
    # Normalize Income / Compute probabilities
    incomes = merged_df[ECONOMIC_DATA_COL].values
    populations = merged_df[POPULATION_DATA_COL].values
    probabilities = populations / populations.sum()
    
    # Endowments array, length len(NUM_AGENTS)
    endowments = np.random.choice(incomes, size=NUM_AGENTS, p=probabilities)
    
    # Map GEO_ID to income
    geo_id_to_income = pd.Series(
        data=merged_df[ECONOMIC_DATA_COL].values,
        index=merged_df['GEO_ID']
    ).to_dict()
    
    print(f"Incomes:")
    print(geo_id_to_income)
    n = (len(geo_id_to_income))
    print(f"Number of tracts used for income distribution calculations: {n}\n")

    return endowments, geo_id_to_income