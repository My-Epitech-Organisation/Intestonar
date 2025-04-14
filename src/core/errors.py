#!/usr/bin/env python3

"""
Error handling module for Interstonar.
Contains custom exceptions and error handling functions.
"""

class InterstonarException(Exception):
    """Base exception class for Interstonar project."""
    pass


class ConfigError(InterstonarException):
    """Exception raised for errors in the configuration file."""
    def __init__(self, message="Invalid configuration file"):
        self.message = message
        super().__init__(self.message)


class ArgumentError(InterstonarException):
    """Exception raised for errors in the command line arguments."""
    def __init__(self, message="Invalid arguments"):
        self.message = message
        super().__init__(self.message)


def handle_error(error, exit_code=84):
    """General error handler that prints to stderr and exits with given code."""
    import sys
    print(f"Error: {error}", file=sys.stderr)
    sys.exit(exit_code)