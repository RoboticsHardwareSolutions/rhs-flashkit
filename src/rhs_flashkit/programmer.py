"""
Base Programmer Abstract Class

This module defines the base abstract class for all programmers.
Each programmer implementation (JLink, ST-Link, etc.) should inherit from this class.
"""

import logging
import subprocess
import time
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


# STM32 DBGMCU_IDCODE register addresses
DBGMCU_IDCODE_ADDRESSES = {
    0x40015800: "STM32G0 series",
    0xE0042000: "Most STM32 series (F1/F4/F7/etc)"
}

# STM32 Device ID mapping (from datasheets)
DEVICE_ID_MAP = {
    # STM32F1 series
    0x412: "STM32F10x Low-density",         # F103C4, F103C6, etc
    0x410: "STM32F10x Medium-density",      # F103C8, F103CB, F103R8, F103RB, etc
    0x414: "STM32F10x High-density",        # F103RC, F103RE, F103VC, F103VE, etc
    0x430: "STM32F10x XL-density",          # F103RF, F103RG, F103VF, F103VG, etc
    0x418: "STM32F10x Connectivity line",   # F105, F107
    0x420: "STM32F10x Medium-density value",
    0x428: "STM32F10x High-density value",
    
    # STM32F4 series
    0x413: "STM32F405xx/407xx/415xx/417xx", # F405, F407, F415, F417
    0x419: "STM32F42xxx/43xxx",             # F427, F429, F437, F439
    
    # STM32F7 series
    0x451: "STM32F76x/77x",                 # F765, F767
    0x449: "STM32F74x/75x",                 # F745, F746, F750, F756
    
    # STM32G0 series
    0x466: "STM32G0x1",                     # G031, G041, G051, G061, G071, G081
    0x460: "STM32G0x0",                     # G030, G050, G070
    0x467: "STM32G0Bx/G0Cx",                # G0B1, G0C1
}

# Default MCU names for each device ID
DEFAULT_MCU_MAP = {
    # F7 series
    0x451: "STM32F765ZG",
    0x449: "STM32F765ZG",
    
    # F4 series
    0x413: "STM32F407VG",
    0x419: "STM32F429ZI",
    
    # F1 series
    0x414: "STM32F103RE",  # High-density
    0x410: "STM32F103C8",  # Medium-density
    0x412: "STM32F103C4",  # Low-density
    0x430: "STM32F103RG",  # XL-density
    0x418: "STM32F105RC",  # Connectivity
    
    # G0 series
    0x466: "STM32G071RB",
    0x460: "STM32G070RB",
    0x467: "STM32G0B1RE",
}


class Programmer(ABC):
    """Abstract base class for all programmer implementations."""
    
    root_logger = logging.getLogger("Programmer")

    def __init__(self, serial: Optional[str] = None):
        """
        Initialize programmer.
        
        Args:
            serial: Programmer serial number (optional)
        """
        self._serial = serial
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    @abstractmethod
    def flash(self, file_path: str, mcu: Optional[str] = None, do_verify: bool = True, reset: bool = True) -> bool:
        """
        Flash firmware to the device.
        Automatically connects to target if not already connected.
        
        Args:
            file_path: Path to firmware file
            mcu: MCU name (optional, will auto-detect if not provided)
            do_verify: Whether to verify the flash operation
            reset: Whether to reset device after flashing (default: True)
            
        Returns:
            True if flash was successful, False otherwise
        """
        pass

    @abstractmethod
    def probe(self) -> bool:
        """
        Probe/detect if the programmer is connected and accessible.
        
        Returns:
            True if programmer is detected, False otherwise
        """
        pass

    @abstractmethod
    def reset(self, halt: bool = False):
        """
        Reset the target device.
        
        Args:
            halt: Whether to halt after reset
        """
        pass

    @abstractmethod
    def erase(self, mcu: Optional[str] = None) -> bool:
        """
        Erase the target device flash memory.
        
        Args:
            mcu: MCU name (optional, will auto-detect if not provided)
            
        Returns:
            True if erase was successful, False otherwise
        """
        pass

    @abstractmethod
    def detect_target(self) -> Optional[str]:
        """
        Detect connected MCU device.
            
        Returns:
            Device name or None if detection failed
        """
        pass

    @staticmethod
    def get_target_info(dev_id: int) -> dict:
        """
        Get device information by device ID.
        
        Args:
            dev_id: Device ID (12-bit value from DBGMCU_IDCODE)
            
        Returns:
            Dictionary with 'family' and 'default_mcu' keys
        """
        return {
            'family': DEVICE_ID_MAP.get(dev_id, f"Unknown (0x{dev_id:03X})"),
            'default_mcu': DEFAULT_MCU_MAP.get(dev_id, "Unknown")
        }

    @classmethod
    def _spawn_and_await(cls, process_params: list, show_progress: bool = False) -> subprocess.Popen:
        """
        Spawn a subprocess and wait for it to complete.
        
        Args:
            process_params: List of command and arguments
            show_progress: Whether to show progress dots
            
        Returns:
            Completed subprocess.Popen object
        """
        cls.root_logger.debug(f"Launching: {' '.join(process_params)}")

        process = subprocess.Popen(
            process_params,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        if show_progress:
            while process.poll() is None:
                time.sleep(0.25)
                print(".", end="", flush=True)
            print()
        else:
            process.wait()

        return process

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure disconnection."""
        if hasattr(self, '_disconnect_target'):
            self._disconnect_target()

    def __repr__(self):
        """String representation of the programmer."""
        serial_info = f", serial={self._serial}" if self._serial else ""
        return f"{self.__class__.__name__}({serial_info})"
