#!/usr/bin/env python3

"""
Global simulation module for Interstonar.
Handles gravitational simulation of celestial bodies.
"""

import math
import copy
from src.core.utils import calculate_distance, normalize_vector
from src.core.utils import calculate_volume_sphere, calculate_radius_from_volume
from src.core.physics import (calculate_gravitational_force, calculate_net_force,
                             calculate_acceleration, update_velocity, update_position,
                             merge_bodies, check_all_collisions, is_collision_with_rock)

# Gravitational constant (G)
G = 6.674e-11  # m^3 kg^-1 s^-2

# Time step for simulation (1 hour in seconds)
DELTA_TIME = 3600

# Maximum simulation time (365 days in hours)
MAX_STEPS = 365 * 24

# Rock mass and radius constants
ROCK_MASS = 1.0  # 1kg
ROCK_RADIUS = 1.0  # 1m (small enough for our simulation)


def run_global_simulation(bodies, rock_position, rock_velocity):
    """
    Run global simulation of celestial bodies and a rock.

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
        # 1. Update positions of all celestial bodies
        for body in bodies:
            body["position"] = update_position(body, DELTA_TIME)
            
        # 2. Update rock position
        rock["position"] = update_position(rock, DELTA_TIME)
        
        # 3. Display rock position at this step
        print(f"At time t = {step}: rock is ({rock['position']['x']:.3f}, {rock['position']['y']:.3f}, {rock['position']['z']:.3f})")
        
        # 4. Check for collisions between rock and celestial bodies
        collision_result, body_index = check_rock_collisions(bodies, rock)
        if collision_result:
            # Rock collided with a body
            collided_body = bodies[body_index]
            print(f"Collision between rock and {collided_body['name']}")
            
            # Check if the body is a goal
            if "goal" in collided_body and collided_body["goal"]:
                return "Mission success"
            else:
                return "Mission failure"
        
        # 5. Check for collisions between celestial bodies
        body_collisions = check_all_collisions(bodies)
        if body_collisions:
            # Handle collisions (starting from highest indices to avoid issues when removing items)
            body_collisions.sort(reverse=True, key=lambda x: x[0])
            
            for i, j in body_collisions:
                # Create a merged body
                merged_body = merge_bodies(bodies[i], bodies[j])
                
                # Remove the colliding bodies
                bodies.pop(i)
                bodies.pop(j if j > i else j)
                
                # Add the merged body
                bodies.append(merged_body)
                
                print(f"Collision between {merged_body['name']} bodies")
        
        # 6. Calculate net forces on all celestial bodies
        forces = []
        for body in bodies:
            # Create list of other bodies excluding current one
            other_bodies = [b for b in bodies if b != body]
            
            # Add rock to other bodies (rock affects celestial bodies)
            other_bodies.append(rock)
            
            # Calculate net force on this body
            force = calculate_net_force(body, other_bodies)
            forces.append(force)
        
        # 7. Calculate net force on rock (from all celestial bodies)
        rock_force = calculate_net_force(rock, bodies)
        
        # 8. Update velocities based on forces
        for i, body in enumerate(bodies):
            acceleration = calculate_acceleration(forces[i], body["mass"])
            body["direction"] = update_velocity(body, acceleration, DELTA_TIME)
        
        # 9. Update rock velocity
        rock_acceleration = calculate_acceleration(rock_force, rock["mass"])
        rock["direction"] = update_velocity(rock, rock_acceleration, DELTA_TIME)
    
    # If we've reached the maximum number of steps without a collision
    return "Mission failure"


def check_rock_collisions(bodies, rock):
    """
    Check for collisions between the rock and any celestial body.

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