"""Example usage of rhs-flashkit."""

from rhs_flashkit import (
    flash_device_by_usb, 
    auto_detect_device, 
    get_device_info, 
    get_connected_devices,
    get_first_available_device,
    find_device_by_serial
)
import pylink


def example_flash():
    """Example: Flash device with auto-detection."""
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


def example_detect():
    """Example: Detect connected device."""
    serial_number = 123456789  # Your programmer serial number
    
    jlink = pylink.JLink()
    jlink.open(serial_no=serial_number)
    jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
    
    # Auto-detect device
    mcu = auto_detect_device(jlink, verbose=True)
    if mcu:
        print(f"Detected MCU: {mcu}")
    
    jlink.close()


def example_device_info():
    """Example: Get device information by ID."""
    # STM32F765/767 device ID
    info = get_device_info(0x451)
    print(f"Device Family: {info['family']}")
    print(f"Default MCU: {info['default_mcu']}")


def example_list_jlinks():
    """Example: List all connected JLink devices."""
    devices = get_connected_devices('jlink')
    if devices:
        print(f"Found {len(devices)} JLink device(s):")
        for device in devices:
            print(f"  Serial: {device['serial']}")
            if 'product' in device:
                print(f"    Product: {device['product']}")
    else:
        print("No JLink devices found")


def example_find_device():
    """Example: Find specific device and get first available."""
    # Get first available device
    device = get_first_available_device('jlink')
    if device:
        print(f"First available device: {device['serial']}")
    
    # Find specific device by serial
    serial = 123456789
    device = find_device_by_serial(serial, 'jlink')
    if device:
        print(f"Found device with serial {serial}")
    else:
        print(f"Device with serial {serial} not found")


if __name__ == "__main__":
    # Uncomment the example you want to run
    # example_flash()
    # example_detect()
    # example_device_info()
    example_list_jlinks()
    # example_find_device()
