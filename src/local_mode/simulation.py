#!/usr/bin/env python3
import math
from src.core.sdf import sphere_sdf, cylinder_sdf, box_sdf, torus_sdf, ray_march, ray_direction

def run_local_simulation(bodies, position, velocity):
    origin = {
        'x': position['x'],
        'y': position['y'],
        'z': position['z']
    }

    # Calculate the normalized direction vector
    direction = ray_direction(velocity)

    # Call the ray_march function from the core/sdf.py
    result, steps, hit_index = ray_march(origin, direction, bodies)

    for i, step in enumerate(steps[1:], 1):  # Start from index 1, not 0
        print(f"Step {i}: ({step['x']:.2f}, {step['y']:.2f}, {step['z']:.2f})")

    return result