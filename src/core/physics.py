#!/usr/bin/env python3

"""
Physics utility functions for Interstonar.
Primarily used for global simulation calculations related to gravitation and motion.
"""

import math
from src.core.utils import calculate_distance, vector_subtract, vector_scale, vector_add

# Gravitational constant (G)
G = 6.674e-11  # m^3 kg^-1 s^-2

# Time step for simulation (1 hour in seconds)
DELTA_TIME = 3600

# Maximum simulation time (365 days in hours)
MAX_STEPS = 365 * 24


def calculate_gravitational_force(body1, body2):
    """
    Calculate gravitational force between two bodies.

    Args:
        body1 (dict): First body with mass and position
        body2 (dict): Second body with mass and position

    Returns:
        dict: Force vector (x, y, z) acting on body1 due to body2
    """
    # Get positions and masses
    pos1 = body1["position"]
    pos2 = body2["position"]
    m1 = body1["mass"]
    m2 = body2["mass"]

    # Calculate distance and direction
    distance = calculate_distance(pos1, pos2)

    # Avoid division by zero
    if distance == 0:
        return {"x": 0, "y": 0, "z": 0}

    # Calculate direction vector from body1 to body2
    direction = vector_subtract(pos2, pos1)

    # Normalize direction vector
    direction_magnitude = math.sqrt(direction["x"]**2 + direction["y"]**2 + direction["z"]**2)
    unit_direction = {
        "x": direction["x"] / direction_magnitude,
        "y": direction["y"] / direction_magnitude,
        "z": direction["z"] / direction_magnitude
    }

    # Calculate force magnitude using Newton's law of universal gravitation
    force_magnitude = G * m1 * m2 / (distance**2)

    # Calculate force vector
    force_vector = {
        "x": unit_direction["x"] * force_magnitude,
        "y": unit_direction["y"] * force_magnitude,
        "z": unit_direction["z"] * force_magnitude
    }

    return force_vector


def calculate_net_force(target_body, all_bodies):
    """
    Calculate the net gravitational force on a body from all other bodies.

    Args:
        target_body (dict): The body to calculate force on
        all_bodies (list): List of all bodies in the system

    Returns:
        dict: Net force vector (x, y, z) acting on target_body
    """
    net_force = {"x": 0, "y": 0, "z": 0}

    for body in all_bodies:
        # Skip if it's the same body
        if body is target_body:
            continue

        # Calculate gravitational force from this body
        force = calculate_gravitational_force(target_body, body)

        # Add to net force
        net_force["x"] += force["x"]
        net_force["y"] += force["y"]
        net_force["z"] += force["z"]

    return net_force


def calculate_acceleration(force, mass):
    """
    Calculate acceleration using F = ma.

    Args:
        force (dict): Force vector (x, y, z)
        mass (float): Mass of the body

    Returns:
        dict: Acceleration vector (x, y, z)
    """
    return {
        "x": force["x"] / mass,
        "y": force["y"] / mass,
        "z": force["z"] / mass
    }


def update_velocity(body, acceleration, delta_time):
    """
    Update velocity of a body using current acceleration and time step.

    Args:
        body (dict): Body with velocity (direction)
        acceleration (dict): Acceleration vector (x, y, z)
        delta_time (float): Time step in seconds

    Returns:
        dict: Updated velocity vector
    """
    velocity = body["direction"]

    # Apply acceleration for the time step (v = v0 + a*t)
    new_velocity = {
        "x": velocity["x"] + acceleration["x"] * delta_time,
        "y": velocity["y"] + acceleration["y"] * delta_time,
        "z": velocity["z"] + acceleration["z"] * delta_time
    }

    return new_velocity


def update_position(body, delta_time):
    """
    Update position of a body using current velocity and time step.

    Args:
        body (dict): Body with position and velocity (direction)
        delta_time (float): Time step in seconds

    Returns:
        dict: Updated position vector
    """
    position = body["position"]
    velocity = body["direction"]

    # Apply velocity for the time step (p = p0 + v*t)
    new_position = {
        "x": position["x"] + velocity["x"] * delta_time,
        "y": position["y"] + velocity["y"] * delta_time,
        "z": position["z"] + velocity["z"] * delta_time
    }

    return new_position


def merge_bodies(body1, body2):
    """
    Merge two colliding bodies according to project rules.

    Args:
        body1 (dict): First colliding body
        body2 (dict): Second colliding body

    Returns:
        dict: New merged body
    """
    # Sum the masses
    new_mass = body1["mass"] + body2["mass"]

    # Calculate total volume from both bodies
    from src.core.utils import calculate_volume_sphere, calculate_radius_from_volume
    volume1 = calculate_volume_sphere(body1["radius"])
    volume2 = calculate_volume_sphere(body2["radius"])
    new_volume = volume1 + volume2
    new_radius = calculate_radius_from_volume(new_volume)

    # Calculate new position (mean of positions)
    new_position = {
        "x": (body1["position"]["x"] + body2["position"]["x"]) / 2,
        "y": (body1["position"]["y"] + body2["position"]["y"]) / 2,
        "z": (body1["position"]["z"] + body2["position"]["z"]) / 2
    }

    # Calculate new velocity (weighted by mass)
    new_velocity = {
        "x": (body1["direction"]["x"] * body1["mass"] + body2["direction"]["x"] * body2["mass"]) / new_mass,
        "y": (body1["direction"]["y"] * body1["mass"] + body2["direction"]["y"] * body2["mass"]) / new_mass,
        "z": (body1["direction"]["z"] * body1["mass"] + body2["direction"]["z"] * body2["mass"]) / new_mass
    }

    # Determine new name (concatenation in ASCII order)
    name1 = body1["name"]
    name2 = body2["name"]
    new_name = name1 + name2 if name1 < name2 else name2 + name1

    # Determine if new body is a goal
    is_goal = (body1.get("goal", False) or body2.get("goal", False))

    # Create the merged body
    merged_body = {
        "name": new_name,
        "position": new_position,
        "direction": new_velocity,
        "mass": new_mass,
        "radius": new_radius
    }

    # Add goal property if at least one body was a goal
    if is_goal:
        merged_body["goal"] = True

    return merged_body


def is_collision_with_rock(rock_position, rock_radius, body):
    """
    Check if the rock collides with a celestial body.

    Args:
        rock_position (dict): Position of the rock (x, y, z)
        rock_radius (float): Radius of the rock (typically very small)
        body (dict): Celestial body with position and radius

    Returns:
        bool: True if collision occurs, False otherwise
    """
    distance = calculate_distance(rock_position, body["position"])
    return distance <= (rock_radius + body["radius"])


def check_all_collisions(bodies):
    """
    Check for collisions between all pairs of bodies.

    Args:
        bodies (list): List of all bodies in the simulation

    Returns:
        list: List of collision pairs as tuples (i, j) where i < j are indices
    """
    collisions = []

    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            body1 = bodies[i]
            body2 = bodies[j]

            # Calculate distance between bodies
            distance = calculate_distance(body1["position"], body2["position"])

            # Check if distance is less than sum of radii
            if distance <= (body1["radius"] + body2["radius"]):
                collisions.append((i, j))

    return collisions