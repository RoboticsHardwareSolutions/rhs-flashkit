"""
RTT Examples

Examples of using JLink RTT functionality for real-time communication
with embedded devices.
"""

from rhs_flashkit import JLinkProgrammer
import time


def example_basic_rtt():
    """Basic RTT connection and reading."""
    print("=" * 60)
    print("Example 1: Basic RTT Reading")
    print("=" * 60)
    
    # Create programmer (auto-detect serial)
    prog = JLinkProgrammer()
    
    try:
        # Connect to target (auto-detect MCU)
        prog._connect_target()
        
        # Start RTT
        prog.start_rtt(delay=1.0)
        
        print("Reading RTT data for 5 seconds...")
        start = time.time()
        
        while time.time() - start < 5.0:
            data = prog.rtt_read()
            if data:
                print(data.decode('utf-8', errors='replace'), end='', flush=True)
            time.sleep(0.01)
        
        # Cleanup
        prog.stop_rtt()
        prog._disconnect_target()
        
    except Exception as e:
        print(f"Error: {e}")


def example_rtt_with_message():
    """Send a message via RTT and read response."""
    print("\n" + "=" * 60)
    print("Example 2: Send Message via RTT")
    print("=" * 60)
    
    prog = JLinkProgrammer(serial=123456789)  # Replace with your serial
    
    try:
        # Connect with specific MCU
        prog._connect_target(mcu="STM32F765ZG")
        
        # Reset device
        prog.reset(halt=False)
        time.sleep(0.5)
        
        # Start RTT
        prog.start_rtt(delay=1.0)
        
        # Wait a bit for device to be ready
        time.sleep(0.5)
        
        # Send command
        command = b"help\n"
        print(f"Sending: {command.decode('utf-8')}")
        prog.rtt_write(command)
        
        # Read response
        print("Response:")
        time.sleep(1.0)  # Wait for response
        
        data = prog.rtt_read(max_bytes=8192)
        if data:
            print(data.decode('utf-8', errors='replace'))
        else:
            print("No response received")
        
        # Cleanup
        prog.stop_rtt()
        prog._disconnect_target()
        
    except Exception as e:
        print(f"Error: {e}")


def example_rtt_interactive():
    """Interactive RTT session."""
    print("\n" + "=" * 60)
    print("Example 3: Interactive RTT Session")
    print("=" * 60)
    
    prog = JLinkProgrammer()
    
    try:
        # Connect
        prog._connect_target()
        prog.start_rtt(delay=1.0)
        
        print("RTT connected. Type commands (Ctrl+C to exit):")
        
        # Continuous read/write loop
        import sys
        import select
        
        while True:
            # Check if stdin has data (non-blocking)
            if sys.platform != 'win32':
                if select.select([sys.stdin], [], [], 0.01)[0]:
                    line = sys.stdin.readline()
                    if line:
                        prog.rtt_write(line.encode('utf-8'))
            
            # Read RTT output
            data = prog.rtt_read()
            if data:
                print(data.decode('utf-8', errors='replace'), end='', flush=True)
            
            time.sleep(0.01)
        
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        prog.stop_rtt()
        prog._disconnect_target()


def example_rtt_logging():
    """Log RTT output to file."""
    print("\n" + "=" * 60)
    print("Example 4: Log RTT Output to File")
    print("=" * 60)
    
    prog = JLinkProgrammer()
    
    try:
        prog._connect_target()
        prog.start_rtt(delay=1.0)
        
        print("Logging RTT output to 'rtt_log.txt' for 10 seconds...")
        
        with open('rtt_log.txt', 'wb') as log_file:
            start = time.time()
            
            while time.time() - start < 10.0:
                data = prog.rtt_read()
                if data:
                    log_file.write(data)
                    log_file.flush()
                    # Also print to console
                    print(data.decode('utf-8', errors='replace'), end='', flush=True)
                time.sleep(0.01)
        
        print("\n\nLog saved to 'rtt_log.txt'")
        
        prog.stop_rtt()
        prog._disconnect_target()
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Run examples
    # Uncomment the example you want to run
    
    example_basic_rtt()
    
    # example_rtt_with_message()
    # example_rtt_interactive()
    # example_rtt_logging()
