"""Device detection and listing functionality."""

from typing import List, Dict, Any, Optional
from .constants import PROGRAMMER_JLINK


def get_connected_devices(programmer: str = PROGRAMMER_JLINK) -> List[Dict[str, Any]]:
    """
    Get list of all connected devices for specified programmer type.
    
    Args:
        programmer: Programmer type ('jlink', etc.)
        
    Returns:
        List of device information dictionaries
        
    Example:
        >>> devices = get_connected_devices('jlink')
        >>> for device in devices:
        ...     print(f"Serial: {device['serial']}")
    """
    if programmer.lower() == PROGRAMMER_JLINK:
        return _get_jlink_devices()
    else:
        raise ValueError(f"Unsupported programmer: {programmer}")


def _get_jlink_devices() -> List[Dict[str, Any]]:
    """
    Get list of connected JLink devices.
    
    Returns:
        List of dictionaries with device information:
        - serial: Serial number
        - product: Product name (if available)
    """
    try:
        import pylink
        jlink = pylink.JLink()
        emulators = jlink.connected_emulators()
        
        devices = []
        for emu in emulators:
            device_info = {
                'serial': emu.SerialNumber,
                'type': 'jlink'
            }
            if hasattr(emu, 'acProduct'):
                device_info['product'] = emu.acProduct
            devices.append(device_info)
        
        if jlink.opened():
            jlink.close()
            
        return devices
    except Exception as e:
        print(f"Warning: Could not enumerate JLink devices: {e}")
        return []


def find_device_by_serial(serial: int, programmer: str = PROGRAMMER_JLINK) -> Optional[Dict[str, Any]]:
    """
    Find a specific device by serial number.
    
    Args:
        serial: Device serial number
        programmer: Programmer type
        
    Returns:
        Device information dictionary or None if not found
    """
    devices = get_connected_devices(programmer)
    for device in devices:
        if device['serial'] == serial:
            return device
    return None


def get_first_available_device(programmer: str = PROGRAMMER_JLINK) -> Optional[Dict[str, Any]]:
    """
    Get the first available device of specified programmer type.
    
    Args:
        programmer: Programmer type
        
    Returns:
        Device information dictionary or None if no devices found
    """
    devices = get_connected_devices(programmer)
    return devices[0] if devices else None


def print_connected_devices(programmer: str = PROGRAMMER_JLINK) -> None:
    """
    Print information about all connected devices.
    
    Args:
        programmer: Programmer type to list
    """
    devices = get_connected_devices(programmer)
    
    if not devices:
        print(f"No {programmer} devices found.")
        return
    
    print(f"Found {len(devices)} {programmer} device(s):\n")
    for idx, device in enumerate(devices, 1):
        print(f"{idx}. Serial Number: {device['serial']}")
        if 'product' in device:
            print(f"   Product: {device['product']}")

