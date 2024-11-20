from __future__ import absolute_import
from config import EPSILON
import numpy as np


class Agent:
    def __init__(self, i, dow, city, alpha=0.5, car_ownership_rate=0.7):
        self.i = i  # Agent identifier
        self.dow = dow  # Endowment
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

        # Transportation mode (based on car ownership rate)
        self.mode = 'car' if np.random.random() < car_ownership_rate else 'transit'

        self.reset()

    def __hash__(self):
        return hash(self.i)

    def __eq__(self, other):
        return self.i == other.i

    def reset(self):
        # Step 1: Initialize sampling based on amenity densities
        self.weights = np.ones(len(self.city.centroids))
        amenity_weights = self.city.amts_dens / np.sum(self.city.amts_dens)
        self.weights = self.weights * amenity_weights
        self.probabilities = np.array(self.weights / self.weights.sum())
        self.tot_probabilities = self.probabilities.copy()

        # Initialize starting position based on trip generation probabilities
        self.u = np.random.choice(self.city.n, p=self.probabilities)
        self.city.inh_array[self.u].add(self)

    def assign_routes(self, assigned_routes):
        """Step 2: Route modification based on FSM route assignment"""
        self.routes = []
        origin_geoid = self.city.centroids[self.u][4]

        # Filter routes for current mode and origin
        for (o_geoid, d_geoid, mode), volume in assigned_routes.items():
            if mode == self.mode and o_geoid == origin_geoid:
                # Convert destination geoid to index
                dest_idx = next(i for i, c in enumerate(self.city.centroids) if c[4] == d_geoid)
                # Add route with weight proportional to volume
                self.routes.extend([dest_idx] * int(volume))

    def act(self):
        """Step 2: Movement based on FSM distribution and mode"""
        self.prev_u = self.u
        self.city.inh_array[self.u].remove(self)

        if self.routes:
            # Weight routes by both FSM assignment and amenity attractiveness
            route_indices = np.array(self.routes)
            route_probs = self.probabilities[route_indices] * self.city.amts_dens[route_indices]
            route_probs = route_probs / route_probs.sum()  # Normalize

            if len(route_indices) > 0:
                self.u = np.random.choice(route_indices, p=route_probs)
            else:
                self.u = np.random.choice(self.city.n, p=self.probabilities)
        else:
            self.u = np.random.choice(self.city.n, p=self.probabilities)

        self.city.inh_array[self.u].add(self)

    def learn(self):
        """Step 3: Update based on cost calculation"""
        cost = self.calculateCost(self.u)
        self.weights[self.u] *= (1 - EPSILON * cost)

        # Update sampling distribution
        self.probabilities = self.weights / np.sum(self.weights)
        self.tot_probabilities += self.probabilities

    def calculateCost(self, u):
        """Step 3: Cost function with mode-specific adjustments"""
        # Base components
        affordability = (self.dow >= self.city.dow_thr_array[u]).astype(float)
        base_location_cost = self.city.centroid_distances[self.prev_u, u]
        community_cost = np.exp(-self.alpha * np.abs(self.dow - self.city.cmt_array[u]))
        accessibility = np.exp(-(1 - self.alpha) * self.city.amts_dens[u])
        upkeep = self.city.upk_array[u]
        beltline = self.city.beltline_array[u]

        # Mode-specific adjustments
        mode_factor = 1.5 if self.mode == 'transit' else 1.0
        location_cost = base_location_cost * mode_factor

        # Combine costs according to FSM and mode
        cost = 1 - (affordability * upkeep * beltline * location_cost * community_cost * accessibility)
        return cost


class Simulation:
    def __init__(self, city, num_agents):
        self.city = city
        self.agents = [Agent(i, np.random.random(), city) for i in range(num_agents)]
        self.assigned_routes = {}  # Store FSM route assignments

    def step(self):
        """Execute one simulation step"""
        # Step 1: Sample current state
        for agent in self.agents:
            agent.act()

        # Step 2: Apply FSM route assignments
        self.update_routes()

        # Step 3: Calculate costs and update
        for agent in self.agents:
            agent.learn()

    def update_routes(self):
        """Update routes based on FSM assignments"""
        for agent in self.agents:
            agent.assign_routes(self.assigned_routes)

    def reset(self):
        """Reset simulation state"""
        for agent in self.agents:
            agent.reset()
        self.assigned_routes = {}

    def set_routes(self, fsm_routes):
        """Update routes from FSM"""
        self.assigned_routes = fsm_routes
        self.update_routes()