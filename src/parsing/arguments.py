#!/usr/bin/env python3

"""
Command line argument parsing for Interstonar.
"""

import sys
from src.core.errors import ArgumentError, handle_error


def print_help():
    """Display help message and exit."""
    print("USAGE:")
    print("  interstonar [--global | --local] CONFIG_FILE Px Py Pz Vx Vy Vz")
    print("")
    print("DESCRIPTION:")
    print("  --global   Launch program in global scene mode.")
    print("  --local    Launch program in local scene mode.")
    print("  Pi         Position coordinates of the rock (x, y, z).")
    print("  Vi         Velocity vector of the rock (x, y, z).")
    print("  CONFIG_FILE  TOML configuration file describing a scene.")
    sys.exit(0)


def parse_arguments():
    """
    Parse command line arguments and validate them.

    Returns:
        dict: A dictionary containing the parsed arguments:
              - mode: '--global' or '--local'
              - config_file: path to the TOML configuration file
              - position: dict with x, y, z coordinates
              - velocity: dict with x, y, z velocity components

    Raises:
        ArgumentError: If the arguments are invalid.
    """
    args = sys.argv

    # Check for help flag
    if len(args) > 1 and (args[1] == "--help" or args[1] == "-h"):
        print_help()

    # Validate argument count
    if len(args) != 9:
        raise ArgumentError("invalid number of arguments")

    # Extract and validate mode
    mode = args[1]
    if mode not in ("--global", "--local"):
        raise ArgumentError(f"invalid mode {mode}")

    config_file = args[2]

    # Parse position and velocity vectors
    try:
        px, py, pz = map(float, args[3:6])
        vx, vy, vz = map(float, args[6:9])
    except ValueError:
        raise ArgumentError("position and velocity must be numeric (float)")

    return {
        "mode": mode,
        "config_file": config_file,
        "position": {"x": px, "y": py, "z": pz},
        "velocity": {"x": vx, "y": vy, "z": vz}
    }