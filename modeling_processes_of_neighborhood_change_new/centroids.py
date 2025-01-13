#centroids.py

import tqdm

def create_centroids(gdf):
    """ Initialize centroids based on rows in Geodataframe"""
    centroids = []
    
    for _, row in tqdm.tqdm(gdf.iterrows(), total=len(gdf), desc="Regions"):
        # Retrieve attributes
        ID = str(row['Simulation_ID'])
        
        beltline_score = row['Beltline Score']
        
        name = row['Simulation_Name']
        
        geometry = row['geometry']
        
        centroid = geometry.centroid
        
        centroids.append((centroid.x, centroid.y, name, beltline_score, ID))
        
        if geometry.is_empty or geometry is None:
            print(f"No geometries found for ID '{ID}'. Skipping centroid creation for this ID.")
            continue  # Skip to the next ID
        
    len_centroids = len(centroids)
    print(f'{len_centroids} centroids were created.')
        
    return centroids