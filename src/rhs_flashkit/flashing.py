import sys
import os
import argparse
import logging

from .constants import SUPPORTED_PROGRAMMERS, DEFAULT_PROGRAMMER, PROGRAMMER_JLINK
from .programmer import Programmer
from .jlink_programmer import JLinkProgrammer


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
        
        # Check if programmer is available
        if not prog.probe():
            raise RuntimeError(f"Programmer not found or not accessible")
        
        print(f"Flashing {fw_file}...")
        
        # Flash firmware (will auto-connect, verify, flash, reset, and disconnect)
        if not prog.flash(fw_file, mcu=args.mcu):
            raise RuntimeError("Flash operation failed")
        
        print("\n✓ Flashing completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
