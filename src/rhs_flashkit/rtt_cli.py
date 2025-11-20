"""
JLink RTT CLI

Command-line interface for connecting to JLink RTT and reading/writing data.
"""

import sys
import time
import argparse
from typing import Optional
from .jlink_programmer import JLinkProgrammer


def main():
    """Main entry point for rhs-jlink-rtt command."""
    parser = argparse.ArgumentParser(
        description='Connect to JLink RTT for real-time data transfer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Connect with auto-detect and read for 10 seconds
  rhs-jlink-rtt

  # Specify JLink serial number
  rhs-jlink-rtt --serial 123456789

  # Connect via IP address (MCU not needed)
  rhs-jlink-rtt --ip 192.168.1.100

  # Specify MCU explicitly
  rhs-jlink-rtt --mcu STM32F765ZG

  # Read indefinitely until Ctrl+C
  rhs-jlink-rtt -t 0

  # Send message after connection
  rhs-jlink-rtt --msg "hello\\n"

  # Send message after 2 seconds delay
  rhs-jlink-rtt --msg "test" --msg-timeout 2.0

  # No reset on connection
  rhs-jlink-rtt --no-reset
        """
    )
    
    parser.add_argument('--serial', '-s', type=str, default=None,
                       help='JLink serial number (auto-detect if not provided)')
    
    parser.add_argument('--ip', type=str, default=None,
                       help='JLink IP address for network connection (e.g., 192.168.1.100)')
    
    parser.add_argument('--mcu', '-m', type=str, default=None,
                       help='MCU name (e.g., STM32F765ZG). Auto-detects if not provided. Not used with --ip.')
    
    parser.add_argument('--reset', dest='reset', action='store_true', default=True,
                       help='Reset target after connection (default: True)')
    
    parser.add_argument('--no-reset', dest='reset', action='store_false',
                       help='Do not reset target after connection')
    
    parser.add_argument('--timeout', '-t', type=float, default=10.0,
                       help='Read timeout in seconds. 0 means read until interrupted (default: 10.0)')
    
    parser.add_argument('--msg', type=str, default=None,
                       help='Message to send via RTT after connection')
    
    parser.add_argument('--msg-timeout', type=float, default=0.5,
                       help='Delay in seconds before sending message (default: 0.5)')
    
    parser.add_argument('--msg-retries', type=int, default=10,
                       help='Number of retries for sending message (default: 10)')
    
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate that --serial and --ip are mutually exclusive
    if args.serial and args.ip:
        print("Error: Cannot specify both --serial and --ip")
        sys.exit(1)
    
    # Convert serial to int if provided
    serial = None
    if args.serial:
        try:
            serial = int(args.serial)
        except ValueError:
            print(f"Error: Invalid serial number: {args.serial}")
            sys.exit(1)
    
    ip_addr = args.ip
    
    try:
        # Create programmer instance
        if args.verbose:
            print(f"Creating JLink programmer (serial={serial}, ip={ip_addr})...")
        
        prog = JLinkProgrammer(serial=serial, ip_addr=ip_addr)
        
        # Connect to target
        # When using IP, MCU is not specified (will use generic connection)
        mcu = None if ip_addr else args.mcu
        if args.verbose:
            print(f"Connecting to target (mcu={mcu})...")
        
        if not prog._connect_target(mcu=mcu):
            print("Error: Failed to connect to target")
            sys.exit(1)
        
        # Reset if requested
        if args.reset:
            if args.verbose:
                print("Resetting target...")
            prog.reset(halt=False)
            time.sleep(0.5)  # Give device time to restart
        
        # Start RTT
        if args.verbose:
            print("Starting RTT...")
        
        if not prog.start_rtt(delay=1.0):
            print("Error: Failed to start RTT")
            prog._disconnect_target()
            sys.exit(1)
        
        print("RTT connected. Reading data...")
        if args.timeout == 0:
            print("(Press Ctrl+C to stop)")
        else:
            print(f"(Reading for {args.timeout} seconds)")
        
        # Send message if provided
        if args.msg:
            time.sleep(args.msg_timeout)
            if args.verbose:
                print(f"Sending message: {repr(args.msg)}")
            
            # Convert escape sequences
            msg = args.msg.encode('utf-8').decode('unicode_escape').encode('utf-8')
            
            # Try to send with retries
            max_retries = args.msg_retries
            retry_delay = 1.0
            bytes_written = 0
            
            for attempt in range(max_retries):
                bytes_written = prog.rtt_write(msg)
                if bytes_written > 0:
                    if args.verbose:
                        print(f"Wrote {bytes_written} bytes" + (f" (attempt {attempt + 1})" if attempt > 0 else ""))
                    break
                
                if attempt < max_retries - 1:
                    if args.verbose:
                        print(f"Write failed (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
            else:
                print(f"Warning: Failed to write message after {max_retries} attempts")
        
        # Read data
        start_time = time.time()
        try:
            while True:
                # Check timeout
                if args.timeout > 0:
                    elapsed = time.time() - start_time
                    if elapsed >= args.timeout:
                        break
                
                # Read RTT data
                data = prog.rtt_read(max_bytes=4096)
                
                if data:
                    # Print data to stdout
                    try:
                        text = data.decode('utf-8', errors='replace')
                        print(text, end='', flush=True)
                    except Exception:
                        # If decode fails, print raw bytes
                        print(data, flush=True)
                
                # Small delay to avoid busy-waiting
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        
        # Cleanup
        if args.verbose:
            print("\nStopping RTT...")
        prog.stop_rtt()
        
        if args.verbose:
            print("Disconnecting...")
        prog._disconnect_target()
        
        print("\nDone.")
        
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
