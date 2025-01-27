import numpy as np
import pandas as pd
from scipy import stats
from config import NUM_AGENTS, ECONOMIC_URL, ECONOMIC_DATA_SKIP_ROWS, ECONOMIC_DATA_COL, POPULATION_URL, \
    POPULATION_DATA_COL, POPULATION_DATA_SKIP_ROWS
from file_download_manager import download_and_extract_census_data


def economic_distribution():
    # Load and prepare data
    income_data = download_and_extract_census_data(ECONOMIC_URL, 'economic_data.zip', 'economic_data')
    population_data = download_and_extract_census_data(POPULATION_URL, 'population_data.zip', 'population_data')

    income_df = pd.read_csv(income_data, skiprows=ECONOMIC_DATA_SKIP_ROWS, header=0)
    population_df = pd.read_csv(population_data, skiprows=POPULATION_DATA_SKIP_ROWS, header=0)

    # Clean and merge data
    income_df[ECONOMIC_DATA_COL] = pd.to_numeric(income_df[ECONOMIC_DATA_COL], errors='coerce')
    population_df[POPULATION_DATA_COL] = pd.to_numeric(population_df[POPULATION_DATA_COL], errors='coerce')

    merged_df = pd.merge(
        income_df[['GEO_ID', ECONOMIC_DATA_COL]],
        population_df[['GEO_ID', POPULATION_DATA_COL]],
        on='GEO_ID',
        how='inner'
    )
    merged_df = merged_df.dropna(subset=[ECONOMIC_DATA_COL, POPULATION_DATA_COL])

    # Calculate weighted statistics from census data
    weights = merged_df[POPULATION_DATA_COL].values
    incomes = merged_df[ECONOMIC_DATA_COL].values

    weighted_mean = np.average(incomes, weights=weights)
    weighted_std = np.sqrt(np.average((incomes - weighted_mean) ** 2, weights=weights))

    # Generate initial endowments using weighted sampling
    probabilities = weights / weights.sum()
    initial_endowments = np.random.choice(incomes, size=NUM_AGENTS, p=probabilities)

    # Calibrate the distribution
    def calibrate_distribution(endowments, target_mean, target_std):
        current_mean = np.mean(endowments)
        current_std = np.std(endowments)

        # Adjust for mean
        mean_adjusted = endowments - current_mean + target_mean

        # Adjust for standard deviation
        std_adjusted = ((mean_adjusted - target_mean) * (target_std / current_std)) + target_mean

        # Ensure no negative values
        std_adjusted = np.maximum(std_adjusted, 0)

        return std_adjusted

    # Apply calibration
    calibrated_endowments = calibrate_distribution(
        initial_endowments,
        target_mean=weighted_mean,
        target_std=weighted_std
    )

    # Validate calibration
    def validate_calibration(original, calibrated, census_incomes, weights):
        print("\nCalibration Validation:")
        print(f"Census Weighted Mean: {weighted_mean:.2f}")
        print(f"Census Weighted Std: {weighted_std:.2f}")
        print(f"Original Mean: {np.mean(original):.2f}")
        print(f"Original Std: {np.std(original):.2f}")
        print(f"Calibrated Mean: {np.mean(calibrated):.2f}")
        print(f"Calibrated Std: {np.std(calibrated):.2f}")

        # Compare distributions using KS test (see here: https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test).
        census_sample = np.random.choice(census_incomes, size=len(calibrated), p=weights / weights.sum())
        ks_stat, p_value = stats.ks_2samp(calibrated, census_sample)
        print(f"\nKolmogorov-Smirnov test:")
        print(f"KS statistic: {ks_stat:.4f}")
        print(f"p-value: {p_value:.4f}")

    validate_calibration(initial_endowments, calibrated_endowments, incomes, weights)

    # Create GEO_ID to income mapping
    truncated_geo_ids = merged_df['GEO_ID'].astype(str).str[9:]
    geo_id_to_income = pd.Series(
        data=merged_df[ECONOMIC_DATA_COL].values,
        index=truncated_geo_ids
    ).to_dict()

    return calibrated_endowments, geo_id_to_income