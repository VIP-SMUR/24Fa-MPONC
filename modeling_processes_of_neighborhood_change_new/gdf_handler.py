# gdf_handler.py

import geopandas as gpd
import pandas as pd
from config import IDENTIFIER_COLUMNS, NAME_COLUMNS, ID_LIST, viewData
from in_beltline import check_in_beltline

# =======================
# GDF FILE INITIALIZATION
# =======================

def load_gdf(cache_files, beltline_geom):
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
    
    combined_gdf = create_Beltline_column(combined_gdf, beltline_geom)
    
    return combined_gdf, num_geometries, num_geometries_individual

# create new gdf
def create_gdf(shapefile_paths, cache_files, beltline_geom):
    """ Create and modify each layer's Geodataframe, then combine into one Combined Geodataframe """
    gdfs = []
    num_geometries = []
    for i in shapefile_paths:
        shapefile_path = shapefile_paths[i]
        cache_file = cache_files[i]
        
        print(f"Creating GDF file for Layer {i}...")
        gdf = gpd.read_file(shapefile_path)
        
        # Rename identifier column to 'ID'
        gdf = rename_ID_Name_columns(gdf, i)
        
        # Create SQKM column
        gdf = create_Sqkm_column(gdf)
        
        # Set CRS
        gdf = gdf.to_crs(epsg=4326)
        
        # Save to cache
        print(f"Individual GeoDataFrame saved to '{cache_file}'.")
        gdf.to_file(cache_file, driver='GPKG')
        
        if viewData:
            gdf_geom_counts = gdf.geometry.geom_type.value_counts()
            print(gdf_geom_counts)
            print()
        
        gdfs.append(gdf)  
        
        num_geometries.append(len(gdf))
        
        # View individual GDF information
        if viewData:
            print(gdf)
            
    # Combine all gdfs
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
    combined_gdf, num_geometries, num_geometries_individual = within_gdf(combined_gdf)
    
    combined_gdf = create_Beltline_column(combined_gdf, beltline_geom)
    
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
    if identifier_column != 'Simulation_ID':
        gdf = gdf.rename(columns={identifier_column: 'Simulation_ID'})
    if name_column != 'Simulation_Name':
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
def create_Beltline_column(gdf, beltline_geom):
    """ Helper function to create 'Beltline' column """
    print("Updating 'in_beltline' attribute...")
    gdf['Beltline'] = gdf['geometry'].apply(lambda poly: check_in_beltline(poly, beltline_geom))
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

def print_overlaps(gdf):
    # Join GDF with itself to compare the two...
    overlaps = gpd.sjoin(gdf, gdf, how='inner', predicate='overlaps', lsuffix='left', rsuffix='right')
    
    # The left GDF's index is now overlaps.index; the right GDF's index is overlaps['index_right'].
    # Remove self-comparisons by comparing the left index (overlaps.index) with 'index_right'
    overlaps = overlaps[overlaps.index != overlaps['index_right']]

    # Create a unique pair identifier based on the 'Simulation_ID's
    overlaps['sorted_pair'] = overlaps.apply(
        lambda row: tuple(sorted([row['Simulation_ID_left'], row['Simulation_ID_right']])), 
        axis=1
    )

    # Remove duplicate pairs
    overlaps = overlaps.drop_duplicates(subset='sorted_pair')

    if not overlaps.empty:
        print("Overlapping regions:")
        print(overlaps[['Simulation_Name_left', 'Simulation_Name_right', 'Simulation_ID_left', 'Simulation_ID_right']])
        print()
    else:
        print("No overlaps detected")


