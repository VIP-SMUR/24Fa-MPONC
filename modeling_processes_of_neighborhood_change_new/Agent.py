from __future__ import absolute_import
from helper import EPSILON
import numpy as np
import grid2demand as gd

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
        self.routes = None  # To hold assigned routes

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

        # Add self to the current node's set of inhabitants in inh_array
        self.city.inh_array[self.u].add(self)

    # Assign routes to the agent
    def assign_routes(self, assigned_routes):
        # Assigned routes should be a mapping of agents to their routes
        self.routes = assigned_routes.get(self.i, [])

    # ACTION METHOD
    def act(self):
        # Store current node
        self.prev_u = self.u
        
        # Leave current node
        self.city.inh_array[self.u].remove(self)

        # Choose another node based on assigned routes if available, otherwise randomly
        if self.routes:
            # Choose from assigned routes with probabilities based on weights
            self.u = np.random.choice(self.routes, p=self.probabilities[
                self.routes])  # Routes might need a specific way to get probabilities
        else:
            # Random choice among all centroids
            self.u = np.random.choice(self.city.n, p=self.probabilities)

            # Join new node
        self.city.inh_array[self.u].add(self)

    # LEARN METHOD
    def learn(self):
        
        cost = self.calculateCost(self.u) # Calculate cost of self.u
        self.weights[self.u] *= (1 - EPSILON * cost) # Update weight of self.u (based on cost)
        
        # Normalize probabilities
        self.probabilities = self.weights / np.sum(self.weights)
        
        # Accumulate total probabilites (=1?)
        self.tot_probabilities += self.probabilities

    def calculateCost(self, u):
        dow_thr = self.city.dow_thr_array[u]
        aff = (self.dow >= dow_thr).astype(float)  # Affordability: Is the agent's endowment >= endowment threshold?
        loc = self.city.centroid_distances[self.prev_u, u]  # Location cost: Distance from previous to current region
        cmt = np.exp(-self.alpha * np.abs(self.dow - self.city.cmt_array[u]))  # Community cost
        acc = np.exp(-(1 - self.alpha) * self.city.amts_dens[u])  # Accessibility cost
        upk = self.city.upk_array[u]  # Upkeep cost
        beltline = self.city.beltline_array[u]  # Beltline cost

        cost = 1 - aff * upk * beltline * loc * cmt * acc
        return cost
