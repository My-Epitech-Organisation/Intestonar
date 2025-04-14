#!/usr/bin/env python3

"""
Signed Distance Functions (SDFs) and related utilities for Interstonar.
Used in local mode for ray marching and can be useful for collision detection in global mode.
"""

import math
from src.core.utils import vector_subtract, vector_magnitude, vector_dot_product


def sphere_sdf(point, sphere):
    """
    Signed distance function for a sphere.

    Args:
        point (dict): Point coordinates (x, y, z)
        sphere (dict): Sphere definition with position and radius

    Returns:
        float: Signed distance from point to sphere
    """
    center = sphere["position"]
    radius = sphere["radius"]

    # Calculate distance from point to center of sphere
    diff = vector_subtract(point, center)
    distance = vector_magnitude(diff)

    # Return signed distance (negative inside, positive outside)
    return distance - radius


def cylinder_sdf(point, cylinder):
    """
    Signed distance function for a right circular cylinder along the z-axis.

    Args:
        point (dict): Point coordinates (x, y, z)
        cylinder (dict): Cylinder definition with position, radius, and optional height

    Returns:
        float: Signed distance from point to cylinder
    """
    center = cylinder["position"]
    radius = cylinder["radius"]

    # Compute distance in the xy-plane
    dx = point["x"] - center["x"]
    dy = point["y"] - center["y"]
    distance_xy = math.sqrt(dx**2 + dy**2) - radius

    # If height is provided, check bounds along z-axis
    if "height" in cylinder:
        height = cylinder["height"]
        z = point["z"] - center["z"]
        distance_z = abs(z) - height / 2

        # Combine distances using smooth min function
        if distance_z > 0:
            # Outside height bounds
            if distance_xy > 0:
                # Outside radius bounds
                return math.sqrt(distance_xy**2 + distance_z**2)
            else:
                # Inside radius bounds but outside height bounds
                return distance_z
        else:
            # Inside height bounds
            return distance_xy
    else:
        # Infinite cylinder (only consider xy-distance)
        return distance_xy


def box_sdf(point, box):
    """
    Signed distance function for a box parallel to the axes.

    Args:
        point (dict): Point coordinates (x, y, z)
        box (dict): Box definition with position and sides

    Returns:
        float: Signed distance from point to box
    """
    center = box["position"]
    half_sides = {
        "x": box["sides"]["x"] / 2,
        "y": box["sides"]["y"] / 2,
        "z": box["sides"]["z"] / 2
    }

    # Calculate distance components for each axis
    dx = abs(point["x"] - center["x"]) - half_sides["x"]
    dy = abs(point["y"] - center["y"]) - half_sides["y"]
    dz = abs(point["z"] - center["z"]) - half_sides["z"]

    # Outside distance
    outside_dist = math.sqrt(
        max(0, dx)**2 +
        max(0, dy)**2 +
        max(0, dz)**2
    )

    # Inside distance
    inside_dist = min(max(dx, dy, dz), 0)

    return outside_dist + inside_dist


def torus_sdf(point, torus):
    """
    Signed distance function for a torus parallel to the xy-plane.

    Args:
        point (dict): Point coordinates (x, y, z)
        torus (dict): Torus definition with position, inner_radius, and outer_radius

    Returns:
        float: Signed distance from point to torus
    """
    center = torus["position"]
    inner_radius = torus["inner_radius"]
    outer_radius = torus["outer_radius"]

    # Shift point to torus center
    px = point["x"] - center["x"]
    py = point["y"] - center["y"]
    pz = point["z"] - center["z"]

    # Project to xz-plane
    q_xz = math.sqrt(px**2 + py**2) - inner_radius

    # Calculate distance
    return math.sqrt(q_xz**2 + pz**2) - outer_radius


def min_sdf(point, bodies):
    """
    Calculate the minimum SDF for a point against all bodies.

    Args:
        point (dict): Point coordinates (x, y, z)
        bodies (list): List of all bodies in the scene

    Returns:
        tuple: (minimum distance, index of closest body)
    """
    min_dist = float('inf')
    min_index = -1

    for i, body in enumerate(bodies):
        distance = None
        body_type = body["type"]

        if body_type == "sphere":
            distance = sphere_sdf(point, body)
        elif body_type == "cylinder":
            distance = cylinder_sdf(point, body)
        elif body_type == "box":
            distance = box_sdf(point, body)
        elif body_type == "torus":
            distance = torus_sdf(point, body)

        if distance is not None and distance < min_dist:
            min_dist = distance
            min_index = i

    return min_dist, min_index


def ray_direction(velocity):
    """
    Calculate the ray direction from velocity vector.

    Args:
        velocity (dict): Velocity vector (x, y, z)

    Returns:
        dict: Normalized direction vector
    """
    mag = math.sqrt(velocity["x"]**2 + velocity["y"]**2 + velocity["z"]**2)
    if mag == 0:
        return {"x": 0, "y": 0, "z": 0}

    return {
        "x": velocity["x"] / mag,
        "y": velocity["y"] / mag,
        "z": velocity["z"] / mag
    }


def ray_march(origin, direction, bodies, max_steps=1000, min_distance=0.1, max_distance=1000.0):
    """
    Perform ray marching from origin in given direction.

    Args:
        origin (dict): Starting point (x, y, z)
        direction (dict): Direction vector (normalized)
        bodies (list): List of all bodies in the scene
        max_steps (int): Maximum number of steps before timing out
        min_distance (float): Distance threshold for intersection
        max_distance (float): Maximum distance to march

    Returns:
        tuple: (result, steps list, hit_index)
            - result: "Intersection", "Out of scene", or "Time out"
            - steps: List of points visited during marching
            - hit_index: Index of the intersected body or -1
    """
    steps = []
    total_distance = 0.0
    current_point = origin.copy()

    for step in range(max_steps):
        # Calculate minimum signed distance to any object
        dist, hit_index = min_sdf(current_point, bodies)

        # Record current position
        steps.append(current_point.copy())

        # Check for intersection
        if dist <= min_distance:
            return "Intersection", steps, hit_index

        # Check if we're too far
        if dist > max_distance or total_distance > max_distance:
            return "Out of scene", steps, -1

        # Move along the ray by the safe distance
        total_distance += dist
        current_point = {
            "x": current_point["x"] + direction["x"] * dist,
            "y": current_point["y"] + direction["y"] * dist,
            "z": current_point["z"] + direction["z"] * dist
        }

    # We've reached the maximum number of steps without finding anything
    return "Time out", steps, -1