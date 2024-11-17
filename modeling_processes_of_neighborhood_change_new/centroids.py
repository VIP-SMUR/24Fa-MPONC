#centroids.py

def create_centroids(gdf, ID_LIST):
    # Initialize centroids array
    # tuple format: (longitude, latitude, region_name, is_beltline, ID)
    centroids = []
    
    # Initialize centroids
    for ID, is_beltline in ID_LIST[:]:
        # Fetch ID instance from gdf
        gdf_sub = gdf[gdf['ID'] == ID]
        
        if gdf_sub.empty:
            print(f"No geometries found for ID '{ID}'. Skipping centroid creation for this ID.")
            continue  # Skip to the next ID

        # Combined geometry of all geometries in gdf_sub
        combined_geometry = gdf_sub.geometry.unary_union

        # Initialize centroid with coordinates
        centroid = combined_geometry.centroid
        centroids.append((centroid.x, centroid.y, gdf_sub['Name'].iloc[0], is_beltline, ID))
        
        print(f'Centroid: {ID}\n')
        
    return centroids