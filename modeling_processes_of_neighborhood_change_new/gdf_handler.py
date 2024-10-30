# gdf_handler.py

import geopandas as gpd
import pandas as pd
from config import IDENTIFIER_COLUMNS, NAME_COLUMNS

# =======================
# GDF FILE INITIALIZATION
# =======================

def load_gdf(cache_files):
    gdfs = []
    for i in cache_files:
        cache_file = cache_files[i]
        print(f"Loading GeoDataFrame from '{cache_file}...'\n")
        gdf = gpd.read_file(cache_file)
        gdfs.append(gdf)
        
    # Combine all gdfs:
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True)) #TODO: cache?
    return combined_gdf

def create_gdf(shapefile_paths, cache_files):
    gdfs = []
    for i in shapefile_paths:
        shapefile_path = shapefile_paths[i]
        cache_file = cache_files[i]
        if cache_file.exists():
            gdf = gpd.read_file(cache_file)
        else:
            print(f"Creating GDF file for Layer {i}...")
            gdf = gpd.read_file(shapefile_path)
        
            # Simplify geometries
            gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.001, preserve_topology=True)   

            # Add 'Sqkm' area column:
            gdf = gdf.to_crs(epsg=32616)  # Update CRS for area calculations
            gdf['Sqkm'] = gdf['geometry'].area / 1e+6 
            gdf = gdf.to_crs(epsg=4326)
            
            # Rename identifier column to 'ID'
            gdf = rename_columns(gdf, i)
        
            # Save to cache
            print(f"Saving processed GeoDataFrame to '{cache_file}'...\n")
            gdf.to_file(cache_file, driver='GPKG')

        gdfs.append(gdf)
        
    # Combine all gdfs
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    return combined_gdf

def rename_columns(gdf, layer_index):
    identifier_column = IDENTIFIER_COLUMNS.get(layer_index)
    name_column = NAME_COLUMNS.get(layer_index)
    if identifier_column != 'ID':
        gdf = gdf.rename(columns={identifier_column: 'ID'})
    if name_column != 'Name':
        gdf = gdf.rename(columns={name_column: 'Name'})
    return gdf

def print_overlaps(gdf):
    combined_gdf = gdf
    # Filter out 'Atlanta' polygon
    combined_gdf = combined_gdf[combined_gdf['ID'] != '1304000']
    
    # Check for overlaps
    overlaps = gpd.sjoin(combined_gdf, combined_gdf, predicate='overlaps', how='inner')
    
    # Filter out when comparing to itself
    overlaps = overlaps[overlaps['ID_left'] != overlaps['ID_right']]
    
    # Unique pair identifier
    overlaps['sorted_pair'] = overlaps.apply(lambda row: tuple(sorted([row['Name_left'], row['Name_right']])), axis=1)
    # Filter out repeat checks by checking for unique pair identifier
    overlaps = overlaps.drop_duplicates(subset='sorted_pair')
    
    # Drop duplicate pairs based on the sorted pair identifier
    overlaps = overlaps.drop_duplicates(subset='sorted_pair')

    if not overlaps.empty:
        print("Overlapping regions:")
        print(overlaps[['Name_left', 'Name_right']])   
        print()
    else:
        print("No overlaping regions found.")