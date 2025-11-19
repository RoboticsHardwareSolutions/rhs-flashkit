"""Example usage of rhs-flashkit - OOP API."""

from rhs_flashkit import JLinkProgrammer


def example_flash_simple():
    """Example: Flash device with minimal code."""
    firmware_file = "path/to/firmware.hex"
    
    # Flash with auto-detected JLink (first available)
    prog = JLinkProgrammer()
    prog.flash(firmware_file)


def example_flash_with_serial():
    """Example: Flash with specific JLink serial number."""
    firmware_file = "path/to/firmware.hex"
    serial_number = 123456789
    
    prog = JLinkProgrammer(serial=serial_number)
    prog.flash(firmware_file)


def example_flash_with_mcu():
    """Example: Flash with specific MCU specified."""
    firmware_file = "path/to/firmware.hex"
    
    prog = JLinkProgrammer()
    prog.flash(firmware_file, mcu="STM32F765ZG")


def example_flash_no_reset():
    """Example: Flash without reset after programming."""
    firmware_file = "path/to/firmware.hex"
    
    prog = JLinkProgrammer()
    prog.flash(firmware_file, reset=False)


def example_detect_device():
    """Example: Detect connected MCU device."""
    prog = JLinkProgrammer()
    
    # Detect device (requires connection to programmer)
    if prog.probe():
        detected = prog.detect_target()
        if detected:
            print(f"Detected device: {detected}")
        else:
            print("Could not detect device")


def example_reset_device():
    """Example: Reset device after flashing."""
    firmware_file = "path/to/firmware.hex"
    
    prog = JLinkProgrammer()
    
    # Flash without auto-reset
    if prog.flash(firmware_file, reset=False):
        print("Flash successful, performing custom reset...")
        # Do something else here
        prog.reset(halt=False)


def example_read_memory():
    """Example: Read memory from device."""
    prog = JLinkProgrammer()
    
    # Note: Need to connect manually for memory operations
    # (flash() handles connection automatically)
    if hasattr(prog, '_connect_target'):
        prog._connect_target()
        data = prog.read_target_memory(0x08000000, 16)
        if data:
            hex_str = " ".join([f"{b:02X}" for b in data])
            print(f"Memory at 0x08000000: {hex_str}")
        prog._disconnect_target()


if __name__ == "__main__":
    # Uncomment the example you want to run
    
    # Simple usage
    # example_flash_simple()
    
    # With specific serial
    # example_flash_with_serial()
    
    # With specific MCU
    # example_flash_with_mcu()
    
    # Without reset
    # example_flash_no_reset()
    
    # Device detection
    # example_detect_device()
    
    # Custom reset
    # example_reset_device()
    
    # Advanced: Read memory
    # example_read_memory()
