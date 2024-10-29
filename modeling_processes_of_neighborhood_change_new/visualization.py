# visualization.py

# =======================
# VISUALIZATION FUNCTIONS
# =======================

def plot_city(city, g, figkey='final_city'):
    city.plot(cmap='YlOrRd', figkey=figkey, graph=g)
