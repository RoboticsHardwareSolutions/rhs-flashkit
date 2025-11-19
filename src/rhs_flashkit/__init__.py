"""rhs-flashkit - CI/CD toolkit for flashing and testing embedded devices."""

__version__ = "0.1.1"

from .constants import (
    SUPPORTED_PROGRAMMERS,
    DEFAULT_PROGRAMMER,
    PROGRAMMER_JLINK,
)
from .programmer import Programmer
from .jlink_programmer import JLinkProgrammer

__all__ = [
    "SUPPORTED_PROGRAMMERS",
    "DEFAULT_PROGRAMMER",
    "PROGRAMMER_JLINK",
    "Programmer",
    "JLinkProgrammer",
]
