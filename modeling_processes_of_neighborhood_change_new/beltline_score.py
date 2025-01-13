#in_beltline.py

import requests
import geopandas as gpd
from config import HIGH_BLSCORE_METERS, LOW_BLSCORE_METERS
from shapely.geometry import LineString
from shapely.ops import unary_union
from config import RELATION_IDS

# Fetch all nodes that belong to relations
def fetch_beltline_nodes(relation_ids=RELATION_IDS):
    # Custom query based on relation_ids
    query = "[out:json][timeout:180];\n(\n"
    for rel_id in relation_ids:
        query += f"  relation({rel_id});\n"
    query += ");\n(._;>;);\nout body geom;"

    try:
        response = requests.post("http://overpass-api.de/api/interpreter", data={'data': query}) # Query with query through Overpass API
    except Exception as e:
        print(f"Error during Overpass 'Beltline relations' query: {e}")
        return gpd.GeoDataFrame() # Return an empty GDF if query fails

    data = response.json()

    # Build ways[] array
    ways = [elem for elem in data.get('elements', []) if elem['type'] == 'way']
    
    if not ways:
        print("No ways fetched from OSM")

    # Create linestring of coordinates of 'node's within 'way's
    lines = []
    for way in ways:
        if 'geometry' in way:
            coords = [(node['lon'], node['lat']) for node in way['geometry']]
            lines.append(LineString(coords))
        else:
            print(f"Way ID {way.get('id', 'unknown')} missing 'geometry'. Skipping.")

    relations_gdf = gpd.GeoDataFrame(geometry=lines, crs="EPSG:4326")

    print(f"[BELTLINE GDF] created w/ {len(relations_gdf)} 'ways'.")
    
    # Union of geometries in all 'way's in 'relation's
    beltline_geom = unary_union(relations_gdf['geometry'])
    
    return beltline_geom
    
def get_beltline_score(polygon, beltline_geom):
    """ Returns beltline score of a polygon """
    polygon_centroid = polygon.centroid
    dist_meters = polygon_centroid.distance(beltline_geom)
    
    if dist_meters <= HIGH_BLSCORE_METERS:
        return 1.0
    elif dist_meters >= LOW_BLSCORE_METERS:
        return 0.1
    else:
        score =  1.0 - ((dist_meters - HIGH_BLSCORE_METERS) * 0.9 / (LOW_BLSCORE_METERS-HIGH_BLSCORE_METERS))
        return score
    