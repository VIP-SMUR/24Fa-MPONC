from config import viewAmenityData
from helper import AMTS_DENS_CACHE_DIR
import os
import osmnx as ox
import numpy as np
import pickle
import hashlib
import time
import random
from requests.exceptions import RequestException
from tqdm import tqdm


def _hash(*args, **kwargs):
    """Hash function"""
    hasher = hashlib.md5()
    for arg in args:
        hasher.update(pickle.dumps(arg))
    for key, value in sorted(kwargs.items()):
        hasher.update(pickle.dumps((key, value)))
    return hasher.hexdigest()


def fetch_amenities(region_idx, region_polygon, tags, cache_dir=AMTS_DENS_CACHE_DIR, max_retries=3):
    """Fetch amenities for a single region with retry logic and proper error handling"""
    cache_key = f"region_{region_idx}_{_hash(tags=tags)}.npy"
    cache_path = os.path.join(cache_dir, cache_key)

    # Ensure cache directory exists
    os.makedirs(cache_dir, exist_ok=True)

    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except (EOFError, pickle.UnpicklingError):
            # Handle corrupted cache files
            os.remove(cache_path)

    # Add exponential backoff for API requests
    for attempt in range(max_retries):
        try:
            # Add small random delay to prevent API rate limiting
            time.sleep(random.uniform(0.1, 0.5))

            amenities = ox.features_from_polygon(region_polygon, tags=tags)
            amenities_count = len(amenities)

            # Save to cache
            with open(cache_path, 'wb') as f:
                pickle.dump(amenities_count, f)

            return amenities_count

        except RequestException as e:
            if attempt == max_retries - 1:
                print(f"Failed to fetch amenities for region {region_idx} after {max_retries} attempts: {str(e)}")
                return 0
            wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
            time.sleep(wait_time)
        except Exception as e:
            print(f"Unexpected error for region {region_idx}: {str(e)}")
            return 0


def compute_amts_dens(gdf, tags):
    """
    Fetch and compute amenity densities from OSMNX with sequential processing

    Args:
    - gdf: GeoDataFrame containing regions
    - tags: OSM tags to search for amenities

    Returns:
    - Normalized amenity densities per region
    """
    amts_dens = np.zeros(len(gdf))
    amenities_counts = np.zeros(len(gdf))
    areas_sqkm = gdf['Sqkm'].values
    region_names = gdf['Simulation_Name'].values

    print("Fetching amenities per region")

    # Sequential processing with progress bar
    for idx, row in tqdm(gdf.iterrows(), total=len(gdf), desc="Processing Regions"):
        try:
            region_polygon = row['geometry']
            amenities_count = fetch_amenities(idx, region_polygon, tags)

            amenities_counts[idx] = amenities_count
            if areas_sqkm[idx] > 0:
                amts_dens[idx] = amenities_count / areas_sqkm[idx]
            else:
                amts_dens[idx] = 0
        except Exception as e:
            print(f"Error processing region {idx}: {str(e)}")
            amenities_counts[idx] = 0
            amts_dens[idx] = 0

    # Normalize densities
    max_density = amts_dens.max()
    if max_density > 0:
        amts_dens /= max_density

    # View Data?
    if viewAmenityData:
        output_lines = [
            f"{name:<40} {area:>12.2f} {amt:>10}"
            for name, area, amt in zip(region_names, areas_sqkm, amenities_counts)
        ]
        print(f"\n{'[Region]':<40} {'[Area (sq km)]':>12} {'[# Amenities]':>10}")
        print("\n".join(output_lines))

    return amts_dens