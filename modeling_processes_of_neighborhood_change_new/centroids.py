#centroids.py


def create_centroids(gdf, ID_LIST):
    # Initialize centroids array
    centroids = []
    # tuple format: (longitude, latitude, region_name, is_beltline, ID)
    used_IDS = [ID for ID, _ in ID_LIST if ID in set(gdf['ID'])]
    ID_info = {ID: is_beltline for ID, is_beltline in ID_LIST if ID in used_IDS}

    # Iterate through ID_LIST and initialize centroids
    for ID in used_IDS[:-1]:
        # Is_beltline
        is_beltline = ID_info.get(ID, False)

        # Fetch ID instance from combined_gdf
        gdf_sub = gdf[gdf['ID'] == ID]

        # Combined geometry of all geometries in gdf_sub
        combined_geometry = gdf_sub.geometry.union_all()

        # Initialize centroid with coordinates
        centroid = combined_geometry.centroid
        centroids.append((centroid.x, centroid.y, gdf_sub['Name'].iloc[0], is_beltline, ID))
        
    return centroids