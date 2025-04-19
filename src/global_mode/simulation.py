#!/usr/bin/env python3

"""
Global simulation module for Interstonar.
Handles gravitational simulation of celestial bodies and trajectory
of a projectile (rock) through space using Newton's laws of motion.
"""

import math
import copy
from src.core.utils import calculate_distance, normalize_vector
from src.core.utils import calculate_volume_sphere, calculate_radius_from_volume
from src.core.physics import (calculate_gravitational_force, calculate_net_force,
                             calculate_acceleration, update_velocity, update_position,
                             merge_bodies, check_all_collisions, is_collision_with_rock)

# Physical constants
G = 6.674e-11  # Gravitational constant (m^3 kg^-1 s^-2)

# Simulation parameters
DELTA_TIME = 3600  # Time step (1 hour in seconds)
MAX_STEPS = 365 * 24  # Maximum simulation time (365 days)

# Rock properties
ROCK_MASS = 1.0  # Mass of the projectile (1kg)
ROCK_RADIUS = 1.0  # Radius of the projectile (1m)


def run_global_simulation(bodies, rock_position, rock_velocity):
    """
    Run global simulation of celestial bodies and a rock using Newtonian physics.
    
    The simulation uses Euler integration with a fixed time step to calculate
    the trajectories of all bodies, including the rock, under gravitational forces.
    It continues until either the rock collides with a body, or the maximum
    simulation time is reached.

    Args:
        bodies (list): List of bodies from the configuration
        rock_position (dict): Initial position of the rock (x, y, z)
        rock_velocity (dict): Initial velocity of the rock (x, y, z)

    Returns:
        str: Result of simulation ("Mission success" or "Mission failure")
    """
    # Make deep copies to avoid modifying the original data
    bodies = copy.deepcopy(bodies)

    # Create rock object
    rock = {
        "position": copy.deepcopy(rock_position),
        "direction": copy.deepcopy(rock_velocity),
        "mass": ROCK_MASS,
        "radius": ROCK_RADIUS,
        "name": "Rock"
    }

    # Run simulation for up to MAX_STEPS
    for step in range(1, MAX_STEPS + 1):
        # Calculate forces on all bodies
        # These forces will be used to update velocities after position updates
        forces = []
        for body in bodies:
            # Get all bodies that affect the current body (excluding itself)
            other_bodies = [b for b in bodies if b != body]
            
            # Include rock's gravitational effect on celestial bodies
            other_bodies.append(rock)
            
            # Calculate net gravitational force on current body
            force = calculate_net_force(body, other_bodies)
            forces.append(force)

        # Calculate gravitational force on the rock from all celestial bodies
        rock_force = calculate_net_force(rock, bodies)

        # Update positions using current velocities
        for body in bodies:
            body["position"] = update_position(body, DELTA_TIME)
        
        # Update rock position
        rock["position"] = update_position(rock, DELTA_TIME)

        # Display rock position at current time step
        print(f"At time t = {step}: rock is ({rock['position']['x']:.3f}, {rock['position']['y']:.3f}, {rock['position']['z']:.3f})")

        # Check for collisions between rock and celestial bodies
        collision_result, body_index = check_rock_collisions(bodies, rock)
        if collision_result:
            collided_body = bodies[body_index]
            print(f"Collision between rock and {collided_body['name']}")

            # Mission succeeds if the rock collides with a goal body
            if "goal" in collided_body and collided_body["goal"]:
                return "Mission success"
            else:
                return "Mission failure"

        # Check for and handle collisions between celestial bodies
        body_collisions = check_all_collisions(bodies)
        if body_collisions:
            # Process collisions in reverse index order to avoid invalidating indices
            body_collisions.sort(reverse=True, key=lambda x: x[0])

            for i, j in body_collisions:
                # Merge the colliding bodies according to project rules
                merged_body = merge_bodies(bodies[i], bodies[j])

                # Remove the original bodies (in correct order to maintain valid indices)
                bodies.pop(i)
                bodies.pop(j if j > i else j)

                # Add the merged body to the simulation
                bodies.append(merged_body)

                print(f"Collision between {merged_body['name']} bodies")

        # Update velocities using the calculated forces
        for i, body in enumerate(bodies):
            acceleration = calculate_acceleration(forces[i], body["mass"])
            body["direction"] = update_velocity(body, acceleration, DELTA_TIME)

        # Update rock velocity
        rock_acceleration = calculate_acceleration(rock_force, rock["mass"])
        rock["direction"] = update_velocity(rock, rock_acceleration, DELTA_TIME)

    # If simulation reaches MAX_STEPS without any collision with a goal
    return "Mission failure"


def check_rock_collisions(bodies, rock):
    """
    Check for collisions between the rock and any celestial body.
    
    A collision occurs when the distance between the centers of two bodies
    is less than or equal to the sum of their radii.

    Args:
        bodies (list): List of all celestial bodies
        rock (dict): The rock with position and radius

    Returns:
        tuple: (bool, int or None) - (collided, body_index) or (False, None) if no collision
    """
    for i, body in enumerate(bodies):
        if is_collision_with_rock(rock["position"], rock["radius"], body):
            return True, i

    return False, None