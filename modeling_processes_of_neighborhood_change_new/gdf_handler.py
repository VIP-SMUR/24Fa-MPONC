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
        gdf = gpd.read_file(cache_file)
        gdfs.append(gdf)
        
    # Combine all gdfs:
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    combined_gdf, num_geometries, num_geometries_individual = within_gdf(combined_gdf)
    
    return combined_gdf, num_geometries, num_geometries_individual

# create new gdf
def create_gdf(shapefile_paths, cache_files):
    """ Create and modify each layer's Geodataframe, then combine into one Combined Geodataframe """
    gdfs = []
    num_geometries = []
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
        
        num_geometries.append()
        
        # View individual GDF information
        if viewData:
            print(gdf)
            
    # Combine all gdfs
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    combined_gdf, num_geometries, num_geometries_individual = within_gdf(combined_gdf)
    
    # View combined GDF information
    if viewData:
        geometry_counts = combined_gdf.geometry.geom_type.value_counts()
        print("Combined GeoDataFrame:")
        print(geometry_counts)
        print(combined_gdf)
    
    return combined_gdf, num_geometries, num_geometries_individual

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
    num_geometries_individual = []
    
    # Obtain larger target geometries and find contained geometries:
    for target_ID, _ in ID_LIST:
        # Establish target geometry
        target_geometry = gdf[gdf['Simulation_ID'] == target_ID]['geometry'].unary_union
        
        # Obtain all geometries within target geometry (excluding target geometry)
        contained_geometries_individual = gdf[gdf.within(target_geometry) & (gdf['Simulation_ID'] != target_ID)]
        num_geometries_individual.append(len(contained_geometries_individual))
        
        contained_geometries.append(contained_geometries_individual)
        
    filtered_gdf = gpd.GeoDataFrame(pd.concat(contained_geometries, ignore_index=True), crs=gdf.crs)
    
    num_geometries = len(contained_geometries)
    
    return filtered_gdf, num_geometries, num_geometries_individual