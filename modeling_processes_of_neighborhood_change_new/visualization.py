# visualization.py

from config import PLOT_LIBRARY

# =======================
# VISUALIZATION FUNCTIONS
# =======================

def plot_city(city, g, gdf, figkey='final_city'):
    # Get data from city
    df_data = city.get_data()

    # Merge 'GEOID' and 'Avg Endowment' from df_data to gdf
    gdf = gdf.merge(df_data[['GEOID', 'Avg Endowment']], on='GEOID', how='left')
    gdf = gdf.merge(df_data[['GEOID', 'Amt Density']], on='GEOID', how='left')

    # Plot
    if PLOT_LIBRARY == 1:
        city.plot_plt(cmap='YlOrRd', figkey=figkey, graph=g, gdf=gdf)
    else:
        city.plot_folium(cmap='YlOrRd', figkey=figkey, graph=g, gdf=gdf)
