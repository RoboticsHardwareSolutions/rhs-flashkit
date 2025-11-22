"""
Device Erase CLI

Command-line interface for erasing flash memory of embedded devices.
"""

import sys
import argparse
from .jlink_programmer import JLinkProgrammer


def main():
    """Main entry point for rhs-erase command."""
    parser = argparse.ArgumentParser(
        description='Erase flash memory of embedded devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Erase with auto-detected programmer and MCU
  rhs-erase

  # Specify JLink serial number
  rhs-erase --serial 123456789

  # Specify MCU explicitly
  rhs-erase --mcu STM32F765ZG

  # Use IP address for network JLink
  rhs-erase --ip 192.168.1.100
        """
    )
    
    parser.add_argument('--serial', '-s', type=str, default=None,
                       help='JLink serial number (auto-detect if not provided)')
    
    parser.add_argument('--mcu', '-m', type=str, default=None,
                       help='MCU name (e.g., STM32F765ZG). Auto-detects if not provided.')
    
    parser.add_argument('--ip', type=str, default=None,
                       help='JLink IP address for network connection (e.g., 192.168.1.100)')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Convert serial to int if provided
    serial = None
    if args.serial:
        try:
            serial = int(args.serial)
        except ValueError:
            print(f"Error: Invalid serial number: {args.serial}")
            sys.exit(1)
    
    try:
        # Display configuration
        print("Erase Configuration:")
        print("=" * 50)
        
        if args.ip:
            print(f"Programmer: JLink (IP: {args.ip})")
        elif serial:
            print(f"Programmer: JLink")
            print(f"Serial: {serial}")
        else:
            print("Programmer: JLink (auto-detect)")
        
        if args.mcu:
            print(f"MCU: {args.mcu}")
        else:
            print("MCU: Auto-detect")
        
        print("=" * 50)
        print()
        
        # Create programmer instance
        if args.verbose:
            print(f"Creating JLink programmer...")
        
        prog = JLinkProgrammer(serial=serial, ip_addr=args.ip)
        
        # Perform erase
        print("Erasing device flash memory...")
        
        if prog.erase(mcu=args.mcu):
            print("\n✓ Erase completed successfully!")
            sys.exit(0)
        else:
            print("\n✗ Erase failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
