import numpy as np
from .config import EPSILON

# ===========
# AGENT CLASS
# ===========

class Agent:
    # Constructor
    def __init__(self, i, dow, city, alpha=0.5):
        self.i = i
        self.dow = dow
        self.city = city 
        self.alpha = alpha

        self.weights = None
        self.probabilities = None  # Probability to go to each centroid
        self.tot_probabilities = None
        self.avg_probabilities = None
        self.u = None

        self.reset()
        
    # Create hash identifier
    def __hash__(self):
        return hash(self.i)

    def __eq__(self, other): 
        return self.i == other.i

    def reset(self):
        # Initialize weights
        self.weights = np.ones(len(self.city.centroids))
        
        # Initialize probabilities
        self.probabilities = np.array(self.weights / self.weights.sum())
        
        # Initialize tot_probabilities
        self.tot_probabilities = self.probabilities.copy()
        
        # Initialize current node - Initialize starting position at random node (based on weights)
        self.u = np.random.choice(self.city.n, p=self.probabilities) 
        
        # Adds self to the current node's set of inhabitants in inh_array
        self.city.inh_array[self.u].add(self)

    # ACTION METHOD
    def act(self): 
        # Leave node
        self.city.inh_array[self.u].remove(self)

        # Choose another node
        self.u = np.random.choice(self.city.n, p=self.probabilities) 

        # Join node
        self.city.inh_array[self.u].add(self)
        
    # LEARN METHOD
    def learn(self):
        costs = self.cost_vector()
        self.weights *= (1 - EPSILON * costs)  # array of weights, based on COST
        self.probabilities = self.weights / np.sum(self.weights)  # normalize
        self.tot_probabilities += self.probabilities
        
    def cost_vector(self):
        dow_thr = self.city.dow_thr_array
        
        aff = (self.dow >= dow_thr).astype(float)  # Affordability: Is the agent's endowment >= endowment threshold?
        loc = self.city.centroid_distances[self.u, :]  # Location cost: Distances from centroid to all other centroids
        cmt = np.exp(- self.alpha * np.abs(self.dow - self.city.cmt_array))  # Community cost
        acc = np.exp(- (1 - self.alpha) * self.city.amts_dens)  # Accessibility cost
        upk = self.city.upk_array  # Upkeep cost
        beltline = self.city.beltline_array  # Beltline cost
        
        cost = 1 - aff * upk * beltline * loc * cmt * acc
        return cost