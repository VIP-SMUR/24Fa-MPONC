from __future__ import absolute_import
from helper import EPSILON
import numpy as np


class Agent:
    def __init__(self, i, dow, city, alpha=0.5):
        self.i = i  # Agent identifier
        self.dow = dow  # Day of week
        self.city = city  # City object
        self.alpha = alpha  # Weight parameter for cost calculation

        # Step 1: Initialize sampling variables
        self.weights = None
        self.probabilities = None
        self.tot_probabilities = None
        self.avg_probabilities = None

        # Step 2: Location tracking
        self.u = None  # Current location
        self.prev_u = None  # Previous location
        self.routes = None  # Assigned routes

        self.reset()

    def __hash__(self):
        return hash(self.i)

    def __eq__(self, other):
        return self.i == other.i

    def reset(self):
        # Step 1: Initialize sampling
        self.weights = np.ones(len(self.city.centroids))
        self.probabilities = np.array(self.weights / self.weights.sum())
        self.tot_probabilities = self.probabilities.copy()

        # Initialize starting position based on sampling distribution
        self.u = np.random.choice(self.city.n, p=self.probabilities)
        self.city.inh_array[self.u].add(self)

    def assign_routes(self, assigned_routes):
        """Step 2: Route modification based on assigned paths"""
        self.routes = assigned_routes.get(self.i, [])

    def act(self):
        """Step 2: Movement based on sampling distribution"""
        # Store previous location
        self.prev_u = self.u

        # Leave current location
        self.city.inh_array[self.u].remove(self)

        # Choose next location based on routes or probabilities
        if self.routes:
            route_probs = self.probabilities[self.routes]
            route_probs = route_probs / route_probs.sum()  # Normalize probabilities for routes
            self.u = np.random.choice(self.routes, p=route_probs)
        else:
            self.u = np.random.choice(self.city.n, p=self.probabilities)

        # Join new location
        self.city.inh_array[self.u].add(self)

    def learn(self):
        """Step 3: Update based on cost calculation"""
        cost = self.calculateCost(self.u)
        self.weights[self.u] *= (1 - EPSILON * cost)

        # Update sampling distribution
        self.probabilities = self.weights / np.sum(self.weights)
        self.tot_probabilities += self.probabilities

    def calculateCost(self, u):
        """Step 3: Cost function C = f(a_j, c_j, p_trans)"""
        # Calculate individual cost components
        affordability = (self.dow >= self.city.dow_thr_array[u]).astype(float)
        location_cost = self.city.centroid_distances[self.prev_u, u]
        community_cost = np.exp(-self.alpha * np.abs(self.dow - self.city.cmt_array[u]))
        accessibility = np.exp(-(1 - self.alpha) * self.city.amts_dens[u])
        upkeep = self.city.upk_array[u]
        beltline = self.city.beltline_array[u]

        # Combine costs according to diagram's formula
        cost = 1 - (affordability * upkeep * beltline * location_cost * community_cost * accessibility)
        return cost


class Simulation:
    def __init__(self, city, num_agents):
        self.city = city
        self.agents = [Agent(i, np.random.random(), city) for i in range(num_agents)]
        self.routes = {}  # Dictionary to store agent routes

    def step(self):
        """Execute one simulation step"""
        # Step 1: Sample current state
        for agent in self.agents:
            agent.act()

        # Step 2: Apply modifications (routes)
        self.update_routes()

        # Step 3: Calculate costs and update
        for agent in self.agents:
            agent.learn()

    def update_routes(self):
        """Update routes based on current state"""
        # Implementation depends on routing strategy
        pass

    def reset(self):
        """Reset simulation state"""
        for agent in self.agents:
            agent.reset()
        self.routes = {}