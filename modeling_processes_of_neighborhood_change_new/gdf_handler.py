# gdf_handler.py

import geopandas as gpd
from config import GA_GDF_CACHE_FILE

# =======================
# GDF FILE INITIALIZATION
# =======================

def load_gdf(cache_file=GA_GDF_CACHE_FILE):
    print(f"Loading GeoDataFrame from cache: '{cache_file}'.\n")
    GA_gdf = gpd.read_file(cache_file)
    return GA_gdf

def create_gdf(shapefile_path, cache_file=GA_GDF_CACHE_FILE):
    print(f"Initializing GDF file for the first time.")
    GA_gdf = gpd.read_file(shapefile_path)

    # Simplify geometries
    GA_gdf['geometry'] = GA_gdf['geometry'].simplify(tolerance=0.001, preserve_topology=True)    

    # Add 'Sqkm' area column:
    GA_gdf = GA_gdf.to_crs(epsg=32616)  # Update CRS for area calculations
    GA_gdf['Sqkm'] = GA_gdf['geometry'].area / 1e+6 
    
    # Update CRS for general calculations (ex. amenity retrieval)
    GA_gdf = GA_gdf.to_crs(epsg=4326)
    
    # Save to cache
    print(f"Saving processed GeoDataFrame to cache: '{cache_file}'.\n")
    GA_gdf.to_file(cache_file, driver='GPKG')  # Using GeoPackage for better compatibility
    
    return GA_gdf
