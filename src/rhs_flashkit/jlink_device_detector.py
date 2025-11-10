"""
STM32 Device Detector Module

This module provides functionality to automatically detect STM32 devices
by reading the DBGMCU_IDCODE register through JLink interface.

Usage:
    from jlink_device_detector import detect_stm32_device, auto_detect_device
    
    jlink = pylink.JLink()
    jlink.open(serial_no=123456)
    
    # Auto-detect already connected device
    mcu_name = detect_stm32_device(jlink)
    
    # Or auto-detect and connect in one step
    mcu_name = auto_detect_device(jlink)
"""

import pylink
from pylink import JLink
from typing import Optional


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


def detect_stm32_device(jlink: JLink, verbose: bool = True) -> Optional[str]:
    """
    Detect STM32 device by reading DBGMCU_IDCODE register.
    
    Args:
        jlink: Connected JLink instance
        verbose: If True, print detection progress
        
    Returns:
        Device name like 'STM32F765ZG' or 'STM32F103RE', or None if detection failed
    """
    try:
        # Try to read device ID from different addresses
        idcode = 0
        found_addr = None
        
        for addr, desc in DBGMCU_IDCODE_ADDRESSES.items():
            try:
                idcode = jlink.memory_read32(addr, 1)[0]
                if idcode != 0 and idcode != 0xFFFFFFFF:
                    if verbose:
                        print(f"✓ Read IDCODE from 0x{addr:08X} ({desc})")
                    found_addr = addr
                    break
                else:
                    if verbose:
                        print(f"✗ Address 0x{addr:08X} returned invalid IDCODE (0x{idcode:08X}) - skipping {desc}")
            except Exception as e:
                if verbose:
                    print(f"✗ Cannot read from 0x{addr:08X} ({desc}): {e}")
                continue
        
        if idcode == 0 or idcode == 0xFFFFFFFF or found_addr is None:
            if verbose:
                print("::error::Could not read valid IDCODE from any known address")
            return None
        
        # Extract device and revision IDs
        dev_id = (idcode >> 0) & 0xFFF
        rev_id = (idcode >> 16) & 0xFFFF
        
        if verbose:
            print(f"Detected Device ID: 0x{dev_id:03X}, Revision ID: 0x{rev_id:04X}")
        
        # Get device family name
        device_family = DEVICE_ID_MAP.get(dev_id, f"Unknown (0x{dev_id:03X})")
        if verbose:
            print(f"Device Family: {device_family}")
        
        # Get default MCU name for this device ID
        mcu_name = DEFAULT_MCU_MAP.get(dev_id)
        
        if mcu_name is None:
            # Return generic name based on family if no specific default
            mcu_name = device_family.replace(" ", "_")
        
        return mcu_name
        
    except Exception as e:
        if verbose:
            print(f"Warning: Could not detect device automatically: {e}")
        return None


def auto_detect_device(jlink: JLink, verbose: bool = True) -> Optional[str]:
    """
    Auto-detect STM32 device and establish connection.
    
    Tries to connect with different Cortex-M cores (M0/M3/M4/M7) and auto-detects 
    the device by reading DBGMCU_IDCODE register.
    
    Args:
        jlink: Opened JLink instance (not yet connected)
        verbose: If True, print connection progress
        
    Returns:
        Device name like 'STM32F765ZG' or 'STM32F103RE', or None if failed
    """
    if verbose:
        print("Attempting to connect and detect device...")
    
    # Try to connect with different Cortex-M cores
    # Order: M0 -> M3 -> M4 -> M7 (from simplest to most complex)
    connected = False
    for core in ['Cortex-M0', 'Cortex-M3', 'Cortex-M4', 'Cortex-M7']:
        try:
            jlink.connect(core, verbose=False)
            connected = True
            if verbose:
                print(f"Connected using {core}")
            break
        except:
            continue
    
    if not connected:
        if verbose:
            print("::error::Could not connect with any Cortex-M core")
        return None
    
    # Detect device
    detected_mcu = detect_stm32_device(jlink, verbose=verbose)
    
    return detected_mcu


def get_device_info(dev_id: int) -> dict:
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
