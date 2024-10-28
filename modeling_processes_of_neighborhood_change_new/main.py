# main.py

from .config import DATA_DIR, GA_GDF_CACHE_FILE, GEOIDS, GRAPH_FILE, CTY_KEY, PLOT_CITIES, RHO_L, ALPHA_L, T_MAX_L
from .download_extract import download_file, extract_file
from .gdf_handler import load_gdf, create_gdf
from .graph_handler import load_graph, create_graph, save_graph
from .amtdens_distances import compute_amts_dens, compute_centroid_distances
from .simulation import run_simulation
from .visualization import plot_city
from tqdm import tqdm
import pickle

def main():
    # ========================
    # DOWNLOAD AND EXTRACT ZIP
    # ========================
    file_path = download_file()
    
    # Extract file
    if file_path:
        extracted_path = extract_file(file_path)
    else:
        print("Data download failed. Exiting.")
        return

    # =======================
    # GDF FILE INITIALIZATION
    # =======================
    
    # Load or create GeoDataFrame
    if GA_GDF_CACHE_FILE.exists():
        print("Using cached GeoDataFrame.")
        GA_gdf = load_gdf()
    else:
        shapefile_path = extracted_path / 'Geographic_boundaries,_ACS_2022.shp'  # Define shapefile path
        GA_gdf = create_gdf(shapefile_path)
    
    # =========================
    # GRAPH FILE INITIALIZATION
    # =========================
    
    # Load or create Graph
    if GRAPH_FILE.exists():
        # Load existing graph and its GEOIDs
        g, saved_GEOIDS = load_graph()
        
        # Populate used_GEOIDS based on current valid GEOIDs in GA_gdf
        used_GEOIDS = [geoid for geoid, _ in GEOIDS if geoid in set(GA_gdf['GEOID'])]
        
        # Compare saved_GEOIDS with current GEOIDs
        if set(saved_GEOIDS) != set(used_GEOIDS):
            print("GEOIDs have changed. Recreating the graph...")
            g, used_GEOIDS = create_graph(GA_gdf, GEOIDS)
            save_graph(g, used_GEOIDS)
        else:
            print("Graph already exists. Using cached graph.")
    else:
        # Create new graph
        print("Creating graph for the first time.")
        g, used_GEOIDS = create_graph(GA_gdf, GEOIDS)
        save_graph(g, used_GEOIDS)
    
    # =========================
    # COMPUTE AMENITY DENSITIES
    # =========================
    
    amts_dens = compute_amts_dens(GA_gdf, used_GEOIDS)
    
    # ===============================
    # COMPUTE CENTROID DISTANCES
    # ===============================
    
    # Initialize centroids
    centroids = []
    # tuple format: (longitude, latitude, region_name, is_beltline)
    
    GEOID_info = {geoid: is_beltline for geoid, is_beltline in GEOIDS}
    
    # ===================================
    # CENTROID INITIALIZATION FROM GEOIDS
    # ===================================
    for geoid in tqdm(used_GEOIDS[:-1], desc="\nInitializing Centroids", unit="centroid"):
        # Default is_beltline to False if it's not in tuple
        is_beltline = GEOID_info.get(geoid, False)
        
        # Fetch GEOID instance from GA_gdf
        gdf_sub = GA_gdf[GA_gdf['GEOID'] == geoid]
        
        # Combined geometry of all geometries in gdf_sub
        combined_geometry = gdf_sub.geometry.union_all()
        
        # Initialize centroid with coordinates
        centroid = combined_geometry.centroid
        centroids.append((centroid.x, centroid.y, gdf_sub['Name'].iloc[0], is_beltline))
    
    # Compute centroid distances
    centroid_distances = compute_centroid_distances(centroids, g, used_GEOIDS)
    
    # ====================
    # RUN SIMULATION
    # ====================
    
    run_simulation(centroids, g, amts_dens, centroid_distances)
    
    # ============================
    # PLOT SIMULATION RESULTS
    # ============================
    
    if PLOT_CITIES:
        for rho in RHO_L:
            for alpha in ALPHA_L:
                for t_max in T_MAX_L:
                    pickle_filename = f"{CTY_KEY}_{rho}_{alpha}_{t_max}.pkl"
                    pickle_path = DATA_DIR / pickle_filename
                    if pickle_path.exists():
                        with open(pickle_path, 'rb') as file:
                            city = pickle.load(file)
                        figkey = f"{CTY_KEY}_{rho}_{alpha}_{t_max}"
                        plot_city(city, g, figkey=figkey)
                    else:
                        print(f"Pickle file '{pickle_filename}' does not exist. Skipping plotting.")
                    
if __name__ == "__main__":
    main()