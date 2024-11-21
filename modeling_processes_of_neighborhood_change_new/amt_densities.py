# amtsdens_distances.py
from multiprocessing import Pool, cpu_count

from config import viewData
from helper import AMTS_DENS_CACHE_DIR
import os
import osmnx as ox
import numpy as np
import pickle
import hashlib
from tqdm import tqdm

def _hash(*args, **kwargs):
    """ Hash function """
    hasher = hashlib.md5()
    for arg in args:
        hasher.update(pickle.dumps(arg))
    for key, value in sorted(kwargs.items()):
        hasher.update(pickle.dumps((key, value)))
    return hasher.hexdigest()

def fetch_amenities(region_idx, region_polygon, tags, cache_dir=AMTS_DENS_CACHE_DIR):
    """ Fetch amenities for a single region. Utilize caching to avoid redundant calls """
    cache_key = f"region_{region_idx}_{_hash(tags=tags)}.npy"
    cache_path = os.path.join(cache_dir, cache_key)
    
    if os.path.exists(cache_path):
        # Fetch from cache
        with open(cache_path, 'rb') as f:
            amenities_count = pickle.load(f)
        return amenities_count
    else:
        # Calculate from OSM
        try:
            amenities = ox.features_from_polygon(region_polygon, tags=tags)
            amenities_count = len(amenities)
            # Save to cache
            with open(cache_path, 'wb') as f:
                pickle.dump(amenities_count, f)
        except:
            amenities_count = 0
    
    return amenities_count


def process_single_region(args):
    """Helper function to process a single region for multiprocessing"""
    idx, row, tags = args
    region_polygon = row['geometry']
    amenities_count = fetch_amenities(idx, region_polygon, tags)
    return idx, amenities_count


def compute_amts_dens(gdf, tags):
    """ Fetch and compute amenity densities from OSMNX """
    amts_dens = np.zeros(len(gdf))
    amenities_counts = np.zeros(len(gdf))
    areas_sqkm = gdf['Sqkm'].values
    region_names = gdf['Simulation_Name'].values

    print("Fetching amenities per region.")

    # Prepare arguments for parallel processing
    process_args = [(idx, row, tags) for idx, row in gdf.iterrows()]

    # Process regions in parallel using all but one CPU core
    n_processes = max(1, cpu_count() - 1)
    with Pool(processes=n_processes) as pool:
        results = list(tqdm(
            pool.imap(process_single_region, process_args),
            total=len(gdf),
            desc="Regions"
        ))

    # Process results
    for idx, amenities_count in results:
        amenities_counts[idx] = amenities_count
        if areas_sqkm[idx] > 0:
            amts_dens[idx] = amenities_count / areas_sqkm[idx]
        else:
            amts_dens[idx] = 0  # Avoid division by zero

    # Normalize densities
    max_density = amts_dens.max()
    if max_density > 0:
        amts_dens /= amts_dens.max()

    # View Data?
    if viewData:
        output_lines = [
            f"{name:<40} {area:>12.2f} {amt:>10}" for name, area, amt in zip(region_names, areas_sqkm, amenities_counts)
        ]
        print(f"{'[Region]':<40} {'[Area (sq km)]':>12} {'[# Amenities]':>10}")
        print("\n".join(output_lines))

    return amts_dens

# Notes:
#   - Overpass API does not allow concurrent calls
#   - Limit size of region to query amenities from; do region by region