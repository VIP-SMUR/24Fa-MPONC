# gdf_handler.py

import geopandas as gpd
import pandas as pd
from config import IDENTIFIER_COLUMNS, NAME_COLUMNS, ID_LIST
from helper import used_IDS
import matplotlib.pyplot as plt

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
    
    combined_gdf = combined_gdf.to_crs(epsg=4326)
    
    # Create gdf consisting only of regions in ID_LIST
    combined_gdf = combined_gdf[combined_gdf['ID'].isin(used_IDS)].reset_index(drop=True)
    
    return combined_gdf

gdfs = []
# create new gdf
def create_gdf(shapefile_paths, cache_files):
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
            
            # Rename identifier column to 'ID'
            gdf = rename_ID_column(gdf, i)
            
            # TODO
            # Obtain larger target geometries and find contained geometries:
            for target_region_ID, _ in ID_LIST:
                target_geometry = gdf[gdf['ID'] == target_region_ID]['geometry'].unary_union
                
                # Obtain all geometries within, excluding actual target geometry
                contained_geometries_gdf = gdf[gdf.within(target_geometry) & (gdf['ID'] != target_region_ID)]
                print(f"ID {target_region_ID} contains {len(contained_geometries_gdf)} geometries.") 
            
            # Save to cache
            print(f"Saving processed GeoDataFrame to '{cache_file}'...\n")
            gdf.to_file(cache_file, driver='GPKG')
            
            # Define CRS
            contained_geometries_gdf = contained_geometries_gdf.to_crs(epsg=4326)
            
            # Store manipulated GDF's
            gdfs.append(contained_geometries_gdf)  
    
    # Combine all gdfs
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

    # Set CRS
    combined_gdf = combined_gdf.to_crs(epsg=4326)
    
    combined_gdf = create_SQKM_column(combined_gdf)
    
    geometry_counts = combined_gdf.geometry.geom_type.value_counts()
    print(geometry_counts)
    
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
    return gdf

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