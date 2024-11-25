#in_beltline.py

import requests
import geopandas as gpd
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

    print(f"Created Beltline GeoDataFrame with {len(relations_gdf)} BeltLine 'ways'.\n")
    
    # Union of geometries in all 'way's in 'relation's
    beltline_geom = unary_union(relations_gdf['geometry'])
    
    return beltline_geom
    
def check_in_beltline(polygon, geom):
    return 1 if polygon.intersects(geom) else 0