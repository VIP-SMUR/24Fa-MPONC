# gdf_handler.py

import geopandas as gpd
import pandas as pd
from config import IDENTIFIER_COLUMNS, NAME_COLUMNS, ID_LIST, viewData
from helper import GDF_CACHE_FILENAME, GDF_NUM_GEOMETRIES_FILE, GDF_NUM_GEOMETRIES_INDIVIDUAL_FILE, GDF_CACHE_DIR
from beltline_score import get_beltline_score
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
import pickle

# =======================
# GDF FILE INITIALIZATION
# =======================

def load_gdf():
    """ Load each layer's Geodataframe from cache"""
    # Load GDF if cached:
    if Path(GDF_CACHE_FILENAME).exists():
        gdf = gpd.read_file(GDF_CACHE_FILENAME)
    
    # Load num_geometries and num_geometries_individual if cached
    if Path(GDF_NUM_GEOMETRIES_FILE).exists():
        with open(GDF_NUM_GEOMETRIES_FILE, 'rb') as f:
            num_geometries = pickle.load(f)
    if Path(GDF_NUM_GEOMETRIES_FILE).exists():
        with open(GDF_NUM_GEOMETRIES_INDIVIDUAL_FILE, 'rb') as f:
            num_geometries_individual = pickle.load(f)
    if viewData:
        print("[COMBINED GDF]:")      
        print_info(gdf)
    
    return gdf, num_geometries, num_geometries_individual

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
        
        # Create 'Beltline Score' column
        gdf = create_Beltline_column(gdf, beltline_geom)
        
        if viewData:
            print(f"\n[GDF {i}]:")
            print_info(gdf)
            gdf_to_csv(gdf, i)
        
        # add to 'gdfs' array
        gdfs.append(gdf)  
        # track num_geometries in each gdf
        num_geometries.append(len(gdf))
            
    # Combine all gdfs
    combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    combined_gdf, num_geometries, num_geometries_individual = within_gdf(combined_gdf)
    
    # View combined GDF information
    if viewData:
        print("\n[COMBINED GDF]:")
        print_info(combined_gdf)
        gdf_to_csv(gdf, 0)
        
    # Cache combined GDF 
    print(f"GeoDataFrame saved to '{GDF_CACHE_FILENAME}'.")
    combined_gdf.to_file(GDF_CACHE_FILENAME, driver='GPKG')
    
    # Cache num_geometries & num_geometries_individual
    with open(GDF_NUM_GEOMETRIES_FILE, 'wb') as file:
        pickle.dump(num_geometries, file)
    with open(GDF_NUM_GEOMETRIES_INDIVIDUAL_FILE, 'wb') as file:
        pickle.dump(num_geometries_individual, file)
    
    return combined_gdf, num_geometries, num_geometries_individual

def rename_ID_Name_columns(gdf, layer_index):
    """ Helper function to rename 'identifier' column """
    identifier_column = IDENTIFIER_COLUMNS.get(layer_index)
    name_column = NAME_COLUMNS.get(layer_index)
    
    # Check for 2010 name versions
    if identifier_column not in gdf.columns:
        if identifier_column + "10" in gdf.columns:
            identifier_column = identifier_column + "10"
    if name_column not in gdf.columns:
        if name_column + "10" in gdf.columns:
            name_column = name_column + "10"
    
    # Rename
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
    """ Helper function to create 'Beltline Score' column """
    print("Updating 'Beltline Score'...")
    gdf = gdf.to_crs(epsg=32616) # Meter-based projection
    reprojected_beltline_geom = reproject_geometry(beltline_geom)
    gdf['Beltline Score'] = gdf['geometry'].apply(lambda poly: get_beltline_score(poly, reprojected_beltline_geom))
    gdf = gdf.to_crs(epsg=4326)
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
        print("No overlaps detected.")


def reproject_geometry(geom):
    """ Reprojects a geometry from CRS 4326(OSM lat/lon based) to 32616 (meter based)"""
    geom_gdf = gpd.GeoSeries([geom], crs="EPSG:4326")
    geom_gdf = geom_gdf.to_crs("EPSG:32616")
    return geom_gdf.iloc[0] # reprojected GDF's geometry

def print_info(gdf):
    print("GDF information:")
    print(gdf.geometry.geom_type.value_counts())
    print(gdf.info())
    print(gdf)
    print()
    
def gdf_to_csv(gdf, i):
    # Drop the geometry column
    df_no_geometry = gdf.drop(columns="geometry")
    # Export to CSV
    df_no_geometry.to_csv(GDF_CACHE_DIR / f"GDF_{i}.csv", index=False)