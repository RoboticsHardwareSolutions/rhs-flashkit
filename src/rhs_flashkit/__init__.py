"""rhs-flashkit - CI/CD toolkit for flashing and testing embedded devices."""

__version__ = "0.1.0"

from .flashing import flash_device_by_usb
from .jlink_device_detector import (
    detect_stm32_device,
    auto_detect_device,
    get_device_info,
)
from .list_devices import (
    get_connected_devices,
    get_first_available_device,
    find_device_by_serial,
    print_connected_devices,
)
from .constants import (
    SUPPORTED_PROGRAMMERS,
    DEFAULT_PROGRAMMER,
    PROGRAMMER_JLINK,
)

__all__ = [
    "flash_device_by_usb",
    "get_connected_devices",
    "get_first_available_device",
    "find_device_by_serial",
    "print_connected_devices",
    "detect_stm32_device",
    "auto_detect_device",
    "get_device_info",
    "SUPPORTED_PROGRAMMERS",
    "DEFAULT_PROGRAMMER",
    "PROGRAMMER_JLINK",
]
