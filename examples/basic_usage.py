"""Example usage of rhs-flashkit - both functional and OOP APIs."""

from rhs_flashkit import (
    flash_device_by_usb,
    JLinkProgrammer,
    target,
)


def example_flash_functional():
    """Example: Flash device using functional API (simple)."""
    firmware_file = "path/to/firmware.hex"
    
    # Flash with auto-detected JLink (first available)
    flash_device_by_usb(fw_file=firmware_file)
    
    # Or with specific serial number
    serial_number = 123456789
    flash_device_by_usb(serial=serial_number, fw_file=firmware_file)
    
    # Or specify programmer explicitly
    flash_device_by_usb(serial=serial_number, fw_file=firmware_file, programmer="jlink")
    
    # Or with specific MCU
    flash_device_by_usb(serial=serial_number, fw_file=firmware_file, mcu="STM32F765ZG", programmer="jlink")


def example_flash_oop():
    """Example: Flash device using OOP API (more control)."""
    firmware_file = "path/to/firmware.hex"
    
    # Create programmer instance
    with JLinkProgrammer() as programmer:
        # Check if available
        if not programmer.probe():
            print("No JLink found!")
            return
        
        # Connect (auto-detect MCU)
        if programmer.connect():
            print(f"Connected to: {programmer.get_mcu()}")
            
            # Flash firmware
            if programmer.flash(firmware_file, do_verify=True):
                print("Flash successful!")
                
                # Reset device
                programmer.reset(halt=False)
            else:
                print("Flash failed!")


def example_flash_oop_with_serial():
    """Example: Flash with specific serial using OOP API."""
    serial_number = 123456789
    firmware_file = "path/to/firmware.hex"
    
    # Create programmer with specific serial
    programmer = JLinkProgrammer(serial=serial_number)
    
    try:
        if programmer.probe():
            # Connect with specific MCU
            if programmer.connect(mcu="STM32F765ZG"):
                print(f"Connected to {programmer.get_mcu()}")
                programmer.flash(firmware_file)
                programmer.reset()
    finally:
        programmer.disconnect()


def example_detect_device():
    """Example: Detect connected device using OOP API."""
    with JLinkProgrammer() as programmer:
        if programmer.connect():
            # Get detected MCU
            print(f"Connected MCU: {programmer.get_mcu()}")
            
            # Detect device details
            detected = programmer.detect_device(verbose=True)
            if detected:
                print(f"Detected device: {detected}")


def example_target_info():
    """Example: Get device information by ID."""
    # STM32F765/767 device ID
    info = target.get_info(0x451)
    print(f"Device Family: {info['family']}")
    print(f"Default MCU: {info['default_mcu']}")


def example_list_jlinks():
    """Example: List all connected JLink devices."""
    # Using OOP API
    devices = JLinkProgrammer.get_connected_devices()
    if devices:
        print(f"Found {len(devices)} JLink device(s):")
        for device in devices:
            print(f"  Serial: {device['serial']}")
            if 'product' in device:
                print(f"    Product: {device['product']}")
    else:
        print("No JLink devices found")
    
    # Or use convenience method
    print("\nUsing print_connected_devices():")
    JLinkProgrammer.print_connected_devices()


def example_find_device():
    """Example: Find specific device and get first available."""
    # Get first available device using OOP API
    device = JLinkProgrammer.get_first_available_device()
    if device:
        print(f"First available device: {device['serial']}")
    
    # Find specific device by serial
    serial = 123456789
    device = JLinkProgrammer.find_device_by_serial(serial)
    if device:
        print(f"Found device with serial {serial}")
    else:
        print(f"Device with serial {serial} not found")


def example_read_memory():
    """Example: Read memory from device."""
    with JLinkProgrammer() as programmer:
        if programmer.connect():
            # Read 16 bytes from flash base
            data = programmer.read_memory(0x08000000, 16)
            if data:
                hex_str = " ".join([f"{b:02X}" for b in data])
                print(f"Memory at 0x08000000: {hex_str}")


if __name__ == "__main__":
    # Uncomment the example you want to run
    
    # Functional API (simple, one-liner)
    # example_flash_functional()
    
    # OOP API (more control)
    # example_flash_oop()
    # example_flash_oop_with_serial()
    # example_detect_device()
    # example_target_info()
    
    # Device discovery
    example_list_jlinks()
    # example_find_device()
    
    # Advanced features
    # example_read_memory()
