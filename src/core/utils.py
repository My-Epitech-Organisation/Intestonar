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