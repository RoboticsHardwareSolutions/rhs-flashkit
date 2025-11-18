import sys
import os
import argparse
import logging

from .constants import SUPPORTED_PROGRAMMERS, DEFAULT_PROGRAMMER, PROGRAMMER_JLINK
from .programmer import Programmer
from .jlink_programmer import JLinkProgrammer


def flash_device_by_usb(prog: Programmer, fw_file: str, mcu: str = None) -> None:
    """
    Flash a device using specified programmer.
    
    Args:
        prog: Programmer instance
        fw_file: Path to firmware file
        mcu: MCU name (optional, will auto-detect if not provided)
    """
    try:
        # Check if programmer is available
        if not prog.probe():
            raise RuntimeError(f"Programmer not found or not accessible")
        
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
        # Create programmer instance
        if args.programmer.lower() == PROGRAMMER_JLINK:
            prog = JLinkProgrammer(serial=args.serial)
        else:
            raise NotImplementedError(f"Programmer '{args.programmer}' is not yet implemented")
        
        # If no firmware file specified, just list devices and exit
        if args.firmware_file is None:
            return
        
        # Otherwise flash firmware
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
        
        flash_device_by_usb(prog, fw_file, args.mcu)
        print("\n✓ Flashing completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
