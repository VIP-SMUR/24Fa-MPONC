#centroids.py

import tqdm

def create_centroids(gdf):
    """ Initialize centroids based on rows in Geodataframe"""
    centroids = []
    
    for _, row in tqdm.tqdm(gdf.iterrows(), total=len(gdf), desc="Regions"):
        # Retrieve attributes
        ID = str(row['Simulation_ID'])
        
        in_beltline = row['Beltline']
        
        name = row['Simulation_Name']
        
        geometry = row['geometry']
        centroid = geometry.centroid
        
        centroids.append((centroid.x, centroid.y, name, in_beltline, ID))
        
        if geometry.is_empty or geometry is None:
            print(f"No geometries found for ID '{ID}'. Skipping centroid creation for this ID.")
            continue  # Skip to the next ID
        
    len_centroids = len(centroids)
    print(f'{len_centroids} centroids were created.')
        
    return centroids