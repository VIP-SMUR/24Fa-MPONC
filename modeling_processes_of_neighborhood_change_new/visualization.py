# visualization.py

# =======================
# VISUALIZATION FUNCTIONS
# =======================

def plot_city(city, g, gdf, figkey='final_city'):
    # Get data from city
    df_data = city.get_data()

    # Merge 'GEOID' and 'Avg Endowment' from df_data to gdf
    gdf = gdf.merge(df_data[['GEOID', 'Avg Endowment']], on='GEOID', how='left')

    # Plot
    city.plot(cmap='YlOrRd', figkey=figkey, graph=g, gdf=gdf)
