import sys
import os
import argparse

import pylink
from pylink import JLink

from .jlink_device_detector import auto_detect_device
from .constants import SUPPORTED_PROGRAMMERS, DEFAULT_PROGRAMMER, PROGRAMMER_JLINK
from .list_devices import get_connected_devices, get_first_available_device, print_connected_devices


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
    
    if programmer_lower == PROGRAMMER_JLINK:
        _flash_with_jlink(serial, fw_file, mcu)
    else:
        raise NotImplementedError(f"Programmer '{programmer}' is not yet implemented")


def _flash_with_jlink(jlink_serial: int = None, fw_file: str = None, mcu: str = None) -> None:
    """Flash device using JLink programmer."""
    jlink = pylink.JLink()
    
    # If serial not specified, find first available JLink
    if jlink_serial is None:
        print("No serial number specified, searching for connected JLink devices...")
        device = get_first_available_device(PROGRAMMER_JLINK)
        
        if not device:
            raise RuntimeError("No JLink devices found. Please connect a JLink or specify serial number.")
        
        jlink_serial = device['serial']
        print(f"Using JLink with serial: {jlink_serial}")
        
        # Check if multiple devices available
        all_devices = get_connected_devices(PROGRAMMER_JLINK)
        if len(all_devices) > 1:
            print(f"Note: Multiple JLink devices found ({len(all_devices)}). Using first one. Available serials:")
            for dev in all_devices:
                print(f"  - {dev['serial']}")
    
    jlink.open(serial_no=jlink_serial)

    if jlink.opened():
        jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
        
        # If MCU not specified, auto-detect it
        if not mcu:
            mcu = auto_detect_device(jlink, verbose=True)
            if mcu:
                print(f"Auto-detected MCU: {mcu}")
                # Reconnect with specific device
                jlink.close()
                jlink.open(serial_no=jlink_serial)
                jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
            else:
                print("::error::Could not auto-detect MCU")
                jlink.close()
                sys.exit(1)

        jlink.connect(mcu)

        print("Flashing device...")
        result = jlink.flash_file(fw_file, 0x08000000)
        print(f"Flash result: {result}")
        jlink.reset(halt=False)

    jlink.close()

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Flash embedded devices and manage programmers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List connected programmers
  rhs-flash list
  rhs-flash l --programmer jlink
  
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
        "command_or_firmware",
        type=str,
        help="Command ('list' or 'l' to list devices) or path to firmware file (.hex or .bin)"
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
        # Check if command is 'list' or 'l'
        if args.command_or_firmware.lower() in ['list', 'l']:
            print_connected_devices(args.programmer)
            return
        
        # Otherwise treat as firmware file
        fw_file = os.path.abspath(args.command_or_firmware)
        if not os.path.exists(fw_file):
            print(f"Error: Firmware file not found: {fw_file}")
            print(f"If you meant to list devices, use: rhs-flash list")
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
