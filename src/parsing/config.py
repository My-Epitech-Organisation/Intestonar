#!/usr/bin/env python3

"""
Configuration parsing module for Interstonar.
Handles reading and validating TOML configuration files.
"""

try:
    import tomllib as toml
except ImportError:
    import tomli as toml

from src.core.errors import ConfigError, handle_error


def parse_config(config_file, mode):
    """
    Parse a TOML configuration file and validate its content based on mode.

    Args:
        config_file (str): Path to the TOML configuration file
        mode (str): Either '--global' or '--local'

    Returns:
        dict: Dictionary containing the parsed bodies from the configuration

    Raises:
        ConfigError: If the configuration file is invalid
    """
    try:
        with open(config_file, 'rb') as f:
            config = toml.load(f)
    except FileNotFoundError:
        # Ensure this raises ConfigError
        raise ConfigError(f"file {config_file} not found")
    except toml.TOMLDecodeError as e:
        # Ensure this raises ConfigError for invalid TOML
        raise ConfigError(f"invalid TOML file {config_file}: {e}")
    except Exception as e:
        # Consider adding a general exception catch if other file issues occur
        raise ConfigError(f"error reading config file {config_file}: {e}")

    # Verify that the 'bodies' key exists
    if "bodies" not in config:
        # Ensure this raises ConfigError
        raise ConfigError("missing 'bodies' key in configuration file")

    # Get the bodies list from the configuration
    bodies = config["bodies"]

    # Validate bodies based on the simulation mode
    try:
        if mode == "--global":
            validate_global_bodies(bodies)
        elif mode == "--local":
            validate_local_bodies(bodies)
    except ConfigError as e:
        # Re-raise ConfigError if validation fails
        raise e
    except Exception as e:
        # Catch potential unexpected errors during validation
        raise ConfigError(f"validation error in {config_file}: {e}")

    return bodies


def validate_global_bodies(bodies):
    """
    Validate bodies for global simulation mode.

    Args:
        bodies (list): List of body dictionaries from the TOML configuration

    Raises:
        ConfigError: If any body is invalid for global simulation
    """
    if not bodies:
        raise ConfigError("no bodies defined in configuration file")

    has_goal = False

    for i, body in enumerate(bodies):
        # Check required fields for global simulation
        for field in ["name", "position", "direction", "mass", "radius"]:
            if field not in body:
                raise ConfigError(f"missing required field '{field}' for body {i+1}")

        # Validate position and direction fields
        for vector_field in ["position", "direction"]:
            vector = body[vector_field]
            if not isinstance(vector, dict) or not all(key in vector for key in ["x", "y", "z"]):
                raise ConfigError(f"invalid {vector_field} for body {i+1}")

        # Check for the goal field
        if "goal" in body and body["goal"]:
            has_goal = True

    # At least one body must be a goal in global mode
    if not has_goal:
        raise ConfigError("no goal body found in global mode configuration")


def validate_local_bodies(bodies):
    """
    Validate bodies for local simulation mode.

    Args:
        bodies (list): List of body dictionaries from the TOML configuration

    Raises:
        ConfigError: If any body is invalid for local simulation
    """
    if not bodies:
        raise ConfigError("no bodies defined in configuration file")

    for i, body in enumerate(bodies):
        # Check required fields for all local bodies
        if "position" not in body:
            raise ConfigError(f"missing required field 'position' for body {i+1}")
        if "type" not in body:
            raise ConfigError(f"missing required field 'type' for body {i+1}")

        # Validate position field
        position = body["position"]
        if not isinstance(position, dict) or not all(key in position for key in ["x", "y", "z"]):
            raise ConfigError(f"invalid position for body {i+1}")

        # Validate body-specific fields based on type
        body_type = body["type"]
        if body_type == "sphere":
            if "radius" not in body:
                raise ConfigError(f"missing 'radius' for sphere body {i+1}")
        elif body_type == "cylinder":
            if "radius" not in body:
                raise ConfigError(f"missing 'radius' for cylinder body {i+1}")
            # Height is optional for cylinders
        elif body_type == "box":
            if "sides" not in body:
                raise ConfigError(f"missing 'sides' for box body {i+1}")
            sides = body["sides"]
            if not isinstance(sides, dict) or not all(key in sides for key in ["x", "y", "z"]):
                raise ConfigError(f"invalid sides for box body {i+1}")
        elif body_type == "torus":
            if "inner_radius" not in body:
                raise ConfigError(f"missing 'inner_radius' for torus body {i+1}")
            if "outer_radius" not in body:
                raise ConfigError(f"missing 'outer_radius' for torus body {i+1}")
        else:
            raise ConfigError(f"unknown body type '{body_type}' for body {i+1}")