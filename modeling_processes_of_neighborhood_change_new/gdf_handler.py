# gdf_handler.py

import geopandas as gpd
import pandas as pd
from config import IDENTIFIER_COLUMNS, NAME_COLUMNS, ID_LIST, viewData

# =======================
# GDF FILE INITIALIZATION
# =======================

def load_gdf(cache_files):
    """ Load each layer's Geodataframe from cache"""
    # Load if cached:
    gdfs = []
    for i in cache_files:
        cache_file = cache_files[i]
        print(f"Loading GeoDataFrame from '{cache_file}...'")
        gdf = gpd.read_file(cache_file)
        gdfs.append(gdf)
        
    # Combine all gdfs:
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    combined_gdf = within_gdf(combined_gdf)
    
    return combined_gdf

# create new gdf
def create_gdf(shapefile_paths, cache_files):
    """ Create and modify each layer's Geodataframe, then combine into one Combined Geodataframe """
    gdfs = []
    for i in shapefile_paths:
        shapefile_path = shapefile_paths[i]
        cache_file = cache_files[i]
        
        # Fetch and manipulate:    
        print(f"Creating GDF file for Layer {i}...")
        gdf = gpd.read_file(shapefile_path)
        
        # Rename identifier column to 'ID'
        gdf = rename_ID_Name_columns(gdf, i)
        
        # Create SQKM column
        gdf = create_Sqkm_column(gdf)
        
        gdf = create_Beltline_column(gdf)
        
        # Set CRS
        gdf = gdf.to_crs(epsg=4326)
        
        # Save to cache
        print(f"Individual GeoDataFrame saved to '{cache_file}'.")
        gdf.to_file(cache_file, driver='GPKG')
        
        gdf_geom_counts = gdf.geometry.geom_type.value_counts()
        print(gdf_geom_counts)
        print()
        
        gdfs.append(gdf)  
        
        if viewData:
            print(gdf)
            
    # Combine all gdfs
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    combined_gdf = within_gdf(combined_gdf)
    
    # Print GDF information
    if viewData:
        geometry_counts = combined_gdf.geometry.geom_type.value_counts()
        print("Combined GeoDataFrame:")
        print(geometry_counts)
        print(combined_gdf)
    
    return combined_gdf

def rename_ID_Name_columns(gdf, layer_index):
    """ Helper function to rename 'identifier' column """
    identifier_column = IDENTIFIER_COLUMNS.get(layer_index)
    name_column = NAME_COLUMNS.get(layer_index)
    if identifier_column != 'ID':
        gdf = gdf.rename(columns={identifier_column: 'Simulation_ID'})
    if name_column != 'Name':
        gdf = gdf.rename(columns={name_column: 'Simulation_Name'})
    return gdf

# Create 'Sqkm' area column helper function
def create_Sqkm_column(gdf):
    """ Helper function to create 'Sqkm' column """
    gdf = gdf.to_crs(epsg=32616)  # Update CRS for area calculations
    gdf['Sqkm'] = gdf['geometry'].area / 1e+6 
    gdf = gdf.to_crs(epsg=4326)
    return gdf

# TODO
def create_Beltline_column(gdf):
    """ Helper function to create 'Beltline' column """
    gdf['Beltline'] = 1
    return gdf

def within_gdf(gdf):
    """ Helper function to filter Geodataframe for regions within our target region"""
    contained_geometries = []
    # Obtain larger target geometries and find contained geometries:
    for target_ID, _ in ID_LIST:
        # Establish target geometry
        target_geometry = gdf[gdf['Simulation_ID'] == target_ID]['geometry'].unary_union
        
        # Obtain all geometries within target geometry (excluding target geometry)
        contained_geometries_gdf = gdf[gdf.within(target_geometry) & (gdf['Simulation_ID'] != target_ID)]
        print(f"ID {target_ID} contains {len(contained_geometries_gdf)} geometries.")
        
        contained_geometries.append(contained_geometries_gdf)
        
    filtered_gdf = gpd.GeoDataFrame(pd.concat(contained_geometries, ignore_index=True), crs=gdf.crs)
    return filtered_gdf
   
#TODO: 
def remove_overlaps(gdf):
    """ Helper function to only include regions not containing others """
    return gdf
    
#TODO:
def fill_gaps(gdf):
    """ Helper function to fill in empty spaces with polygons from shapefiles 2+ """
    return gdf

def print_overlaps(gdf):
    """ Helper function to print overlapping regions - OUTDATED, FUNCTIONALITY QUESTIONABLE """
    combined_gdf = gdf
    
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