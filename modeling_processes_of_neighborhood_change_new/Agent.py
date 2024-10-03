import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
import pickle
EPSILON = 1e-3

class Agent:

    def __init__(self, i, dow, city, alpha=0.5):

        self.i = i
        self.dow = dow #endowment
        self.city = city #city
        self.alpha = alpha 

        self.weights = None
        self.probabilities = None
        self.tot_probabilities = None
        self.avg_probabilities = None
        self.u = None

        self.reset()

    def __hash__(self):
        return hash(self.i)

    def __eq__(self, other):
        return self.i == other.i

    def reset(self):
        self.weights = np.array([1.0 if not data['amt'] else 0 for _, data in city.g.nodes(data=True)])
        self.probabilities = np.array(self.weights / self.weights.sum())
        self.tot_probabilities = self.probabilities.copy()
        self.u = np.random.choice(self.city.g.nodes(), p=self.probabilities)
        self.city.g.nodes[self.u]['inh'].add(self)

    def act(self): # ACTION METHOD
        self.city.g.nodes[self.u]['inh'].remove(self) #leave centroid
        self.u = np.random.choice(self.city.g.nodes(), p=self.probabilities) 
        self.city.g.nodes[self.u]['inh'].add(self) #join centroid
        
        for centroid in centroids: #update wealth of centroid after agent action
            centroid.updateWealth

    def learn(self):
        for u in self.city.g.nodes():
            if not self.city.g.nodes[u]['amt']:
                self.weights[u] *= (1 - EPSILON * self.cost(u))
        self.probabilities = np.array(self.weights / self.weights.sum())
        self.tot_probabilities += self.probabilities

    def cost(self, u):
        aff = int(self.dow >= self.city.g.nodes[u]['dow_thr'])
        loc = np.exp(- (1 - self.alpha) * self.city.amts_dist[u])
        upk = int(self.city.g.nodes[u]['upk'])
        cmt = np.exp(- self.alpha * np.abs(self.dow - self.city.g.nodes[u]['cmt']))
        c = 1 - aff * loc * upk * cmt
        return c