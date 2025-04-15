#!/usr/bin/env python3

"""
Global simulation module for Interstonar.
Handles gravitational simulation of celestial bodies.
"""

import math
from src.core.utils import calculate_distance, normalize_vector, vector_magnitude
from src.core.utils import calculate_volume_sphere, calculate_radius_from_volume
from src.core.physics import (
    calculate_net_force, calculate_acceleration,
    update_velocity, update_position, check_all_collisions,
    merge_bodies, is_collision_with_rock
)

# Gravitational constant (G)
G = 6.674e-11  # m^3 kg^-1 s^-2

# Time step for simulation (1 hour in seconds)
DELTA_TIME = 3600

# Maximum simulation time (365 days in hours)
MAX_STEPS = 365 * 24

# Rock mass (1kg as specified)
ROCK_MASS = 1.0

# Rock radius (small value for collision detection)
ROCK_RADIUS = 0.5  # meters


def run_global_simulation(bodies, rock_position, rock_velocity):
    """
    Run global simulation of celestial bodies and a rock.

    Args:
        bodies (list): List of bodies from the configuration
        rock_position (dict): Initial position of the rock (x, y, z)
        rock_velocity (dict): Initial velocity of the rock (x, y, z)

    Returns:
        str: Result of simulation ("success" or "failure")
    """
    # Create a rock object
    rock = {
        "name": "Rock",
        "position": rock_position.copy(),
        "direction": rock_velocity.copy(),
        "mass": ROCK_MASS,
        "radius": ROCK_RADIUS
    }

    # Initialize time step counter
    time_step = 0

    # Print initial position (time 0)
    print(f"At time t = {time_step}: rock is "
          f"({rock['position']['x']:.3f}, {rock['position']['y']:.3f}, {rock['position']['z']:.3f})")

    # Main simulation loop
    for time_step in range(1, MAX_STEPS + 1):
        # Check for collisions between celestial bodies
        collisions = check_all_collisions(bodies)

        # Handle collisions (merge bodies)
        if collisions:
            bodies = handle_body_collisions(bodies, collisions)

        # Update all celestial bodies' positions
        for i, body in enumerate(bodies):
            # Calculate net force on this body
            net_force = calculate_net_force(body, bodies)

            # Calculate acceleration
            acceleration = calculate_acceleration(net_force, body["mass"])

            # Update velocity
            body["direction"] = update_velocity(body, acceleration, DELTA_TIME)

            # Update position
            body["position"] = update_position(body, DELTA_TIME)

        # Calculate net force on the rock from all bodies
        net_force_on_rock = calculate_net_force(rock, bodies)

        # Calculate rock acceleration
        rock_acceleration = calculate_acceleration(net_force_on_rock, rock["mass"])

        # Update rock velocity
        rock["direction"] = update_velocity(rock, rock_acceleration, DELTA_TIME)

        # Update rock position
        rock["position"] = update_position(rock, DELTA_TIME)

        # Print rock position at this time step
        print(f"At time t = {time_step}: rock is "
              f"({rock['position']['x']:.3f}, {rock['position']['y']:.3f}, {rock['position']['z']:.3f})")

        # Check for rock collision with any celestial body
        for i, body in enumerate(bodies):
            if is_collision_with_rock(rock["position"], rock["radius"], body):
                print(f"Collision between rock and {body['name']}")
                if body.get("goal", False):
                    return "Mission success"
                else:
                    return "Mission failure"

    # If we reach this point, the rock didn't collide with anything within the time limit
    return "Mission failure"


def handle_body_collisions(bodies, collisions):
    """
    Handle all collisions between celestial bodies.

    Args:
        bodies (list): List of all bodies
        collisions (list): List of collision pairs as tuples (i, j)

    Returns:
        list: Updated list of bodies after merging collided ones
    """
    # Sort collisions in reverse order of body indices to avoid index shifting
    collisions.sort(reverse=True)

    # Process each collision
    for i, j in collisions:
        # Merge the two bodies
        merged_body = merge_bodies(bodies[i], bodies[j])

        # Remove the original bodies
        bodies.pop(j)  # Remove higher index first to preserve ordering
        bodies.pop(i)

        # Add the merged body
        bodies.append(merged_body)

        # Print information about the merger
        print(f"Collision between {merged_body['name'][:-len(merged_body['name'])//2]} and "
              f"{merged_body['name'][len(merged_body['name'])//2:]}")

    return bodies


def check_collisions(bodies, rock):
    """
    Check for collisions between the rock and celestial bodies.

    Args:
        bodies (list): List of all celestial bodies
        rock (dict): The rock with position and radius

    Returns:
        tuple: (collided, body_index, is_goal) or (False, None, None) if no collision
    """
    for i, body in enumerate(bodies):
        if is_collision_with_rock(rock["position"], rock["radius"], body):
            return True, i, body.get("goal", False)

    return False, None, None