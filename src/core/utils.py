#!/usr/bin/env python3

"""
Utility functions for the Interstonar project.
"""

import math


def calculate_distance(pos1, pos2):
    """Calculate the Euclidean distance between two 3D points."""
    dx = pos2['x'] - pos1['x']
    dy = pos2['y'] - pos1['y']
    dz = pos2['z'] - pos1['z']
    return math.sqrt(dx**2 + dy**2 + dz**2)


def normalize_vector(vector):
    """Normalize a 3D vector to unit length."""
    magnitude = math.sqrt(vector['x']**2 + vector['y']**2 + vector['z']**2)
    if magnitude == 0:
        return {'x': 0, 'y': 0, 'z': 0}
    return {
        'x': vector['x'] / magnitude,
        'y': vector['y'] / magnitude,
        'z': vector['z'] / magnitude
    }


def calculate_volume_sphere(radius):
    """Calculate the volume of a sphere."""
    return (4/3) * math.pi * (radius**3)


def calculate_radius_from_volume(volume):
    """Calculate radius from a sphere's volume."""
    return math.pow((3 * volume) / (4 * math.pi), 1/3)


def vector_add(vec1, vec2):
    """Add two 3D vectors."""
    return {
        'x': vec1['x'] + vec2['x'],
        'y': vec1['y'] + vec2['y'],
        'z': vec1['z'] + vec2['z']
    }


def vector_subtract(vec1, vec2):
    """Subtract vec2 from vec1."""
    return {
        'x': vec1['x'] - vec2['x'],
        'y': vec1['y'] - vec2['y'],
        'z': vec1['z'] - vec2['z']
    }


def vector_scale(vec, scalar):
    """Scale a 3D vector by a scalar value."""
    return {
        'x': vec['x'] * scalar,
        'y': vec['y'] * scalar,
        'z': vec['z'] * scalar
    }


def vector_dot_product(vec1, vec2):
    """Calculate the dot product of two 3D vectors."""
    return vec1['x'] * vec2['x'] + vec1['y'] * vec2['y'] + vec1['z'] * vec2['z']


def vector_cross_product(vec1, vec2):
    """Calculate the cross product of two 3D vectors."""
    return {
        'x': vec1['y'] * vec2['z'] - vec1['z'] * vec2['y'],
        'y': vec1['z'] * vec2['x'] - vec1['x'] * vec2['z'],
        'z': vec1['x'] * vec2['y'] - vec1['y'] * vec2['x']
    }


def vector_magnitude(vec):
    """Calculate the magnitude (length) of a 3D vector."""
    return math.sqrt(vec['x']**2 + vec['y']**2 + vec['z']**2)


def vector_distance(vec1, vec2):
    """Calculate the distance between two points represented by vectors."""
    return vector_magnitude(vector_subtract(vec1, vec2))


def vector_reflect(incident, normal):
    """Calculate the reflection of a vector around a normal vector."""
    # Normalize the normal vector
    normal_unit = normalize_vector(normal)

    # Calculate dot product
    dot = vector_dot_product(incident, normal_unit)

    # Reflected vector = incident - 2 * dot * normal
    return vector_subtract(
        incident,
        vector_scale(normal_unit, 2 * dot)
    )


def weighted_average_vector(vectors, weights):
    """
    Calculate weighted average of vectors using their respective weights.

    Args:
        vectors (list): List of vectors
        weights (list): List of corresponding weights

    Returns:
        dict: Weighted average vector
    """
    total_weight = sum(weights)
    weighted_sum = {'x': 0, 'y': 0, 'z': 0}

    for i, vec in enumerate(vectors):
        weight = weights[i]
        weighted_sum['x'] += vec['x'] * weight
        weighted_sum['y'] += vec['y'] * weight
        weighted_sum['z'] += vec['z'] * weight

    return {
        'x': weighted_sum['x'] / total_weight,
        'y': weighted_sum['y'] / total_weight,
        'z': weighted_sum['z'] / total_weight
    }


def average_position(positions):
    """
    Calculate the average position from a list of positions.

    Args:
        positions (list): List of position dictionaries

    Returns:
        dict: Average position
    """
    count = len(positions)
    if count == 0:
        return {'x': 0, 'y': 0, 'z': 0}

    sum_x = sum(pos['x'] for pos in positions)
    sum_y = sum(pos['y'] for pos in positions)
    sum_z = sum(pos['z'] for pos in positions)

    return {
        'x': sum_x / count,
        'y': sum_y / count,
        'z': sum_z / count
    }


def is_point_inside_sphere(point, sphere_center, radius):
    """
    Check if a point is inside a sphere.

    Args:
        point (dict): Point coordinates (x, y, z)
        sphere_center (dict): Sphere center coordinates (x, y, z)
        radius (float): Sphere radius

    Returns:
        bool: True if the point is inside or on the sphere, False otherwise
    """
    distance = calculate_distance(point, sphere_center)
    return distance <= radius


def is_collision(obj1_pos, obj1_radius, obj2_pos, obj2_radius):
    """
    Check if two spherical objects collide.

    Args:
        obj1_pos (dict): Position of first object (x, y, z)
        obj1_radius (float): Radius of first object
        obj2_pos (dict): Position of second object (x, y, z)
        obj2_radius (float): Radius of second object

    Returns:
        bool: True if the objects collide, False otherwise
    """
    distance = calculate_distance(obj1_pos, obj2_pos)
    return distance <= (obj1_radius + obj2_radius)


def format_vector(vector, precision=3):
    """
    Format a vector for display with specified precision.

    Args:
        vector (dict): Vector with x, y, z components
        precision (int): Number of decimal places

    Returns:
        str: Formatted vector string
    """
    return f"({vector['x']:.{precision}f}, {vector['y']:.{precision}f}, {vector['z']:.{precision}f})"


def clamp(value, min_value, max_value):
    """
    Clamp a value between a minimum and maximum.

    Args:
        value (float): Value to clamp
        min_value (float): Minimum allowed value
        max_value (float): Maximum allowed value

    Returns:
        float: Clamped value
    """
    return max(min_value, min(value, max_value))


def degrees_to_radians(degrees):
    """Convert degrees to radians."""
    return degrees * (math.pi / 180)


def radians_to_degrees(radians):
    """Convert radians to degrees."""
    return radians * (180 / math.pi)