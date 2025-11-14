import sys
import os
import argparse
import logging

from .constants import SUPPORTED_PROGRAMMERS, DEFAULT_PROGRAMMER, PROGRAMMER_JLINK
from .programmer import Programmer
from .jlink_programmer import JLinkProgrammer


def _get_programmer_class(programmer_type: str):
    """
    Get programmer class by type.
    
    Args:
        programmer_type: Type of programmer ('jlink', 'stlink', etc.)
        
    Returns:
        Programmer class
        
    Raises:
        NotImplementedError: If programmer type is not yet implemented
    """
    programmer_lower = programmer_type.lower()
    
    if programmer_lower == PROGRAMMER_JLINK:
        return JLinkProgrammer
    else:
        raise NotImplementedError(f"Programmer '{programmer_type}' is not yet implemented")


def flash_device_by_usb(serial: int = None, fw_file: str = None, mcu: str = None, programmer: str = DEFAULT_PROGRAMMER) -> None:
    """
    Flash a device using specified programmer.
    
    Args:
        serial: Programmer serial number (optional, will auto-detect first available)
        fw_file: Path to firmware file
        mcu: MCU name (optional, will auto-detect if not provided)
        programmer: Programmer type (default: 'jlink')
    """
    programmer_lower = programmer.lower()
    
    if programmer_lower not in SUPPORTED_PROGRAMMERS:
        raise ValueError(
            f"Unsupported programmer: {programmer}. "
            f"Currently supported: {', '.join(SUPPORTED_PROGRAMMERS)}"
        )
    
    # Get programmer class
    programmer_class = _get_programmer_class(programmer_lower)
    
    # If serial not specified, find first available device
    if serial is None:
        print(f"No serial number specified, searching for connected {programmer} devices...")
        devices = programmer_class.get_available()
        
        if not devices:
            raise RuntimeError(f"No {programmer} devices found. Please connect a {programmer} or specify serial number.")
        
        serial = devices[0]['serial']
        print(f"Using {programmer} with serial: {serial}")
        
        if len(devices) > 1:
            print(f"Note: Multiple {programmer} devices found ({len(devices)}). Using first one. Available serials:")
            for dev in devices:
                print(f"  - {dev['serial']}")
    
    # Create programmer instance
    prog = programmer_class(serial=serial)
    
    try:
        # Check if programmer is available
        if not prog.probe():
            raise RuntimeError(f"{programmer} with serial {serial} not found or not accessible")
        
        print(f"Connecting to device...")
        
        # Connect to device (with or without MCU specification)
        if not prog.connect_target(mcu=mcu):
            raise RuntimeError(f"Failed to connect to device")
        
        print(f"Connected to: {prog.get_target_mcu()}")
        
        # Flash firmware
        print(f"Flashing {fw_file}...")
        if not prog.flash_target(fw_file, do_verify=True):
            raise RuntimeError("Flash operation failed")
        
        print("Flash completed successfully!")
        
        # Reset device
        print("Resetting device...")
        prog.reset_target(halt=False)
        
    finally:
        # Ensure cleanup
        prog.disconnect_target()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Flash embedded devices and manage programmers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List connected programmers (no firmware file specified)
  rhs-flash
  rhs-flash --programmer jlink
  
  # Flash with auto-detected JLink (first available)
  rhs-flash firmware.hex
  
  # Flash with specific JLink serial
  rhs-flash firmware.hex --serial 123456
  
  # Flash with specific MCU
  rhs-flash firmware.hex --mcu STM32F765ZG
  
  # Specify programmer explicitly
  rhs-flash firmware.hex --programmer jlink --serial 123456
        """
    )
    
    parser.add_argument(
        "firmware_file",
        type=str,
        nargs='?',
        default=None,
        help="Path to firmware file (.hex or .bin). If not specified, lists connected devices."
    )
    
    parser.add_argument(
        "--serial", "-s",
        type=int,
        default=None,
        help="Programmer serial number (optional, will use first available if not specified)"
    )
    
    parser.add_argument(
        "--mcu",
        type=str,
        default=None,
        help="MCU name (e.g., STM32F765ZG). If not provided, will auto-detect"
    )
    
    parser.add_argument(
        "--programmer", "-p",
        type=str,
        default=DEFAULT_PROGRAMMER,
        choices=SUPPORTED_PROGRAMMERS,
        help=f"Programmer type (default: {DEFAULT_PROGRAMMER})"
    )
    
    args = parser.parse_args()
    
    try:
        # If no firmware file specified, list connected devices
        if args.firmware_file is None:
            programmer_class = _get_programmer_class(args.programmer)
            programmer_class.get_available()
            return
        
        # Otherwise treat as firmware file
        fw_file = os.path.abspath(args.firmware_file)
        if not os.path.exists(fw_file):
            print(f"Error: Firmware file not found: {fw_file}")
            print(f"To list connected devices, run: rhs-flash")
            sys.exit(1)
        
        print(f"Programmer: {args.programmer}")
        if args.serial:
            print(f"Serial: {args.serial}")
        print(f"Firmware: {fw_file}")
        if args.mcu:
            print(f"MCU: {args.mcu}")
        print()
        
        flash_device_by_usb(args.serial, fw_file, args.mcu, args.programmer)
        print("\n✓ Flashing completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
