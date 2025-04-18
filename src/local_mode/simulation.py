#!/usr/bin/env python3
import math

def run_local_simulation(bodies, position, velocity):
    # Extract initial position and velocity components
    current_pos = {
        'x': position['x'],
        'y': position['y'],
        'z': position['z']
    }
    dir_x = velocity['x']
    dir_y = velocity['y']
    dir_z = velocity['z']

    # Calculate the direction vector (normalized)
    magnitude = math.sqrt(dir_x**2 + dir_y**2 + dir_z**2)
    if magnitude == 0:
        return "Invalid direction vector (zero magnitude)"
    step_x = dir_x / magnitude
    step_y = dir_y / magnitude
    step_z = dir_z / magnitude
    
    total_distance = 0.0
    steps = 0
    
    while steps < 1000 and total_distance <= 1000.0:
        # Calculate SDF for all bodies and find the minimum
        min_sdf = float('inf')
        for body in bodies:
            # Calculate SDF based on body type
            if body['type'] == 'sphere':
                dx = current_pos['x'] - body['position']['x']
                dy = current_pos['y'] - body['position']['y']
                dz = current_pos['z'] - body['position']['z']
                distance = math.sqrt(dx**2 + dy**2 + dz**2)
                sdf = distance - body['radius']
            
            elif body['type'] == 'cylinder':
                # Radial distance in x-y plane
                dx = current_pos['x'] - body['position']['x']
                dy = current_pos['y'] - body['position']['y']
                radial_dist = math.sqrt(dx**2 + dy**2) - body['radius']
                
                if 'height' in body and body['height'] > 0:
                    # Finite cylinder: check height along z-axis
                    dz = current_pos['z'] - body['position']['z']
                    half_height = body['height'] / 2.0
                    vertical_dist = abs(dz) - half_height
                    sdf = max(radial_dist, vertical_dist)
                else:
                    # Infinite cylinder
                    sdf = radial_dist
            
            elif body['type'] == 'box':
                dx = abs(current_pos['x'] - body['position']['x']) - body['sides']['x'] / 2.0
                dy = abs(current_pos['y'] - body['position']['y']) - body['sides']['y'] / 2.0
                dz = abs(current_pos['z'] - body['position']['z']) - body['sides']['z'] / 2.0
                
                # Calculate SDF for box
                max_dim = max(dx, dy, dz)
                if max_dim < 0:
                    sdf = max_dim  # Inside the box
                else:
                    # Outside, calculate distance to the closest edge or corner
                    dx_clamped = max(dx, 0.0)
                    dy_clamped = max(dy, 0.0)
                    dz_clamped = max(dz, 0.0)
                    sdf = math.sqrt(dx_clamped**2 + dy_clamped**2 + dz_clamped**2)
            
            elif body['type'] == 'torus':
                # Translate to local coordinates
                dx = current_pos['x'] - body['position']['x']
                dy = current_pos['y'] - body['position']['y']
                dz = current_pos['z'] - body['position']['z']
                
                # Project onto x-y plane and adjust for outer radius
                xy_dist = math.sqrt(dx**2 + dy**2)
                q = (xy_dist - body['outer_radius'], dz)
                sdf = math.sqrt(q[0]**2 + q[1]**2) - body['inner_radius']
            
            else:
                continue  # Unknown body type
            
            if sdf < min_sdf:
                min_sdf = sdf
        
        # Check intersection condition
        if min_sdf <= 0.1:
            step_distance = min_sdf
            current_pos['x'] += step_x * step_distance
            current_pos['y'] += step_y * step_distance
            current_pos['z'] += step_z * step_distance
            total_distance += step_distance
            steps += 1
            print(f"Step {steps}: ({current_pos['x']:.2f}, {current_pos['y']:.2f}, {current_pos['z']:.2f})")

            return "Intersection"

        # Check out of scene
        if min_sdf > 1000.0:
            print(f"Step {steps + 1}: ({current_pos['x']:.2f}, {current_pos['y']:.2f}, {current_pos['z']:.2f})")
            return "Out of scene"
        
        # Move along the direction by the minimum SDF
        step_distance = min_sdf
        current_pos['x'] += step_x * step_distance
        current_pos['y'] += step_y * step_distance
        current_pos['z'] += step_z * step_distance
        total_distance += step_distance
        steps += 1
        
        # Print current step
        print(f"Step {steps}: ({current_pos['x']:.2f}, {current_pos['y']:.2f}, {current_pos['z']:.2f})")
    
    # Check termination after loop
    if steps >= 1000:
        return "Time out"
    else:
        return "Out of scene"