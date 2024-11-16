# gdf_handler.py

import geopandas as gpd
import pandas as pd
from config import IDENTIFIER_COLUMNS, NAME_COLUMNS, ID_LIST
from helper import used_IDS

# =======================
# GDF FILE INITIALIZATION
# =======================

# load from cache
def load_gdf(cache_files):
    gdfs = []
    for i in cache_files:
        cache_file = cache_files[i]
        print(f"Loading GeoDataFrame from '{cache_file}...'")
        gdf = gpd.read_file(cache_file)
        gdfs.append(gdf)
        
    # Combine all gdfs:
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    # Create gdf consisting only of regions in ID_LIST
    combined_gdf = combined_gdf[combined_gdf['ID'].isin(used_IDS)].reset_index(drop=True)
    return combined_gdf

# create new gdf
def create_gdf(shapefile_paths, cache_files):
    gdfs = []
    for i in shapefile_paths:
        shapefile_path = shapefile_paths[i]
        cache_file = cache_files[i]
        
        # If cached:
        if cache_file.exists():
            gdf = gpd.read_file(cache_file)
            
        # Fetch and manipulate individual GDF's:    
        else:
            print(f"Creating GDF file for Layer {i}...")
            gdf = gpd.read_file(shapefile_path)
            
            # TODO
            # Filter GDF for specifis regions
            gdf = gdf[combined_gdf['ID'].isin(used_IDS)].reset_index(drop=True)
        
            # Simplify geometries
            gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.001, preserve_topology=True)   
            
            # Rename identifier column to 'ID'
            gdf = rename_ID_column(gdf, i)
            
            # Create 'Sqkm' area column
            create_SQKM_column(gdf)
            
            # Save to cache
            print(f"Saving processed GeoDataFrame to '{cache_file}'...\n")
            gdf.to_file(cache_file, driver='GPKG')

        # Store manipulated GDF's
        gdfs.append(gdf)
        
    # Combine all gdfs
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    return combined_gdf

def rename_ID_column(gdf, layer_index):
    identifier_column = IDENTIFIER_COLUMNS.get(layer_index)
    name_column = NAME_COLUMNS.get(layer_index)
    if identifier_column != 'ID':
        gdf = gdf.rename(columns={identifier_column: 'ID'})
    if name_column != 'Name':
        gdf = gdf.rename(columns={name_column: 'Name'})
    return gdf

def create_SQKM_column(gdf):
    gdf = gdf.to_crs(epsg=32616)  # Update CRS for area calculations
    gdf['Sqkm'] = gdf['geometry'].area / 1e+6 
    gdf = gdf.to_crs(epsg=4326)

def print_overlaps(gdf):
    combined_gdf = gdf
    # Filter out 'Atlanta' polygon
    combined_gdf = combined_gdf[combined_gdf['ID'] != '1304000']
    
    # Check for overlaps
    overlaps = gpd.sjoin(combined_gdf, combined_gdf, predicate='overlaps', how='inner')
    
    # Ignore when comparing to itself
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