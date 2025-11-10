"""Programmer constants and configuration."""

# Supported programmers
PROGRAMMER_JLINK = "jlink"

# List of all supported programmers
SUPPORTED_PROGRAMMERS = [
    PROGRAMMER_JLINK,
    # Future: "stlink", "openocd", etc.
]

# Default programmer
DEFAULT_PROGRAMMER = PROGRAMMER_JLINK
