# four_step_model.py

from collections import defaultdict

import networkx as nx
import numpy as np


def generate_trips(centroids, amts_dens, base_trips=100):
    """
    Estimate trip generation based on amenity scores.

    Parameters:
    centroids (list): List of (lon, lat, region_name, in_beltline, geoid)
    amts_dens (list): List of amenity scores for each zone
    base_trips (int): Base number of trips to scale by amenity scores

    Returns:
    dict: Dictionary mapping geoid to number of generated trips
    """
    trip_counts = {}
    # Normalize amenity scores to sum to 1 for use as probabilities
    total_amenity_score = sum(amts_dens)
    amenity_probabilities = [score / total_amenity_score for score in amts_dens]

    for idx, (lon, lat, region_name, in_beltline, geoid) in enumerate(centroids):
        # Generate trips based on amenity score probability
        trip_counts[geoid] = np.random.poisson(lam=base_trips * amenity_probabilities[idx])

    return trip_counts


def distribute_trips(trip_counts, centroids, amts_dens, centroid_distances):
    """
    Distribute trips using a gravity model based on amenity scores and transportation costs.

    Parameters:
    trip_counts (dict): Dictionary of trips generated from each origin zone
    centroids (list): List of centroid data (lon, lat, region_name, in_beltline, geoid)
    amts_dens (list): List of amenity scores for each zone
    centroid_distances (dict): Dictionary of distances between centroids

    Returns:
    dict: Nested dictionary with origin-destination trip counts
    """
    trip_distribution = {}

    # Create mapping from geoid to index for amenity scores
    geoid_to_index = {centroid[4]: idx for idx, centroid in enumerate(centroids)}

    for origin_geoid, origin_trips in trip_counts.items():
        origin_idx = geoid_to_index[origin_geoid]
        destination_counts = {}

        # Calculate denominator (sum of amenity * friction factors for all destinations)
        denominator = 0
        for dest_centroid in centroids:
            dest_geoid = dest_centroid[4]
            dest_idx = geoid_to_index[dest_geoid]

            # Get transportation cost (distance) between origin and destination
            try:
                distance = centroid_distances[origin_geoid, dest_geoid]
            except IndexError:
                distance = float('inf')

            # Use distance as friction factor F
            friction_factor = 1 / max(distance, 0.1)  # Avoid division by zero

            # Sum A_j * F_ij
            denominator += amts_dens[dest_idx] * friction_factor

        # Calculate trips to each destination
        for dest_centroid in centroids:
            dest_geoid = dest_centroid[4]
            dest_idx = geoid_to_index[dest_geoid]

            # Get transportation cost (distance) between origin and destination
            try:
                distance = centroid_distances[origin_geoid, dest_geoid]
            except IndexError:
                distance = float('inf')

            friction_factor = 1 / max(distance, 0.1)  # Avoid division by zero

            # Calculate T_ij using the formula:
            # T_ij = P_i * (A_j * F_ij) / Σ(A_j * F_ij)
            if denominator > 0:
                trips = origin_trips * (amts_dens[dest_idx] * friction_factor) / denominator
            else:
                trips = 0

            destination_counts[dest_geoid] = trips

        trip_distribution[origin_geoid] = destination_counts

    return trip_distribution


def modal_split(trip_distribution, car_ownership_rate=0.7):
    """
    Perform a modal split on the trip distribution.

    Parameters:
    trip_distribution (dict): Nested dictionary of trips between origins and destinations
    car_ownership_rate (float): Proportion of trips made by car (default 0.7)

    Returns:
    dict: Dictionary containing trips split by mode
    """
    modes = {
        'car': car_ownership_rate,
        'transit': 1 - car_ownership_rate
    }

    split_distribution = defaultdict(lambda: defaultdict(dict))
    for origin, destinations in trip_distribution.items():
        for dest, trips in destinations.items():
            for mode, rate in modes.items():
                split_distribution[origin][dest][mode] = trips * rate

    return split_distribution


def route_assignment(split_distribution, g):
    """
    Assign routes based on the shortest path in the network.

    Parameters:
    split_distribution (dict): Nested dictionary of trips split by mode
    g (networkx.Graph): Transportation network graph with edge weights representing distance

    Returns:
    dict: Dictionary of assigned routes with volumes and paths
    """
    assigned_routes = defaultdict(lambda: {'volume': 0, 'path': None})

    for origin in split_distribution:
        for destination in split_distribution[origin]:
            for mode, trips in split_distribution[origin][destination].items():
                if trips > 0:
                    # Find the shortest path for this O-D pair
                    try:
                        # Assumes edge weights represent distance
                        shortest_path = nx.shortest_path(g, origin, destination, weight='distance')

                        # Create a route key that includes origin, destination, and mode
                        route_key = (origin, destination, mode)

                        # Update assigned routes with volume and path
                        assigned_routes[route_key]['volume'] += trips
                        assigned_routes[route_key]['path'] = shortest_path

                    except nx.NetworkXNoPath:
                        # Handle cases where no path exists between origin and destination
                        print(f"No path found between {origin} and {destination}")
                    except nx.NodeNotFound:
                        # Handle cases where origin or destination nodes are not in the graph
                        print(f"Node not found for route from {origin} to {destination}")

    return dict(assigned_routes)


def run_four_step_model(centroids, g, amts_dens, centroid_distances, base_trips=100, car_ownership_rate=0.7):
    """
    Run the complete four-step transportation model.

    Parameters:
    centroids (list): List of centroid data
    g (networkx.Graph): Transportation network graph
    amts_dens (list): List of amenity scores for each zone
    centroid_distances (dict): Dictionary of distances between centroids
    base_trips (int): Base number of trips to scale by amenity scores
    car_ownership_rate (float): Proportion of trips made by car

    Returns:
    tuple: (trip_counts, trip_distribution, split_distribution, assigned_routes)
    """
    # Step 1: Trip Generation
    trip_counts = generate_trips(centroids, amts_dens, base_trips)

    # Step 2: Trip Distribution
    trip_distribution = distribute_trips(trip_counts, centroids, amts_dens, centroid_distances)

    # Step 3: Modal Split
    split_distribution = modal_split(trip_distribution, car_ownership_rate)

    # Step 4: Route Assignment
    assigned_routes = route_assignment(split_distribution, g)

    return trip_counts, trip_distribution, split_distribution, assigned_routes