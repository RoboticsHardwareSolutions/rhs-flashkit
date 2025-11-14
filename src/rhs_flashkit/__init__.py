"""rhs-flashkit - CI/CD toolkit for flashing and testing embedded devices."""

__version__ = "0.1.0"

from .flashing import flash_device_by_usb
from .constants import (
    SUPPORTED_PROGRAMMERS,
    DEFAULT_PROGRAMMER,
    PROGRAMMER_JLINK,
)
from .programmer import Programmer
from .jlink_programmer import JLinkProgrammer

__all__ = [
    "flash_device_by_usb",
    "SUPPORTED_PROGRAMMERS",
    "DEFAULT_PROGRAMMER",
    "PROGRAMMER_JLINK",
    "Programmer",
    "JLinkProgrammer",
]
