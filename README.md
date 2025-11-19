# rhs-flashkit

CI/CD toolkit for flashing and testing embedded devices.

## Features

- Flash embedded devices (currently supports JLink)
- List and detect connected programmers
- Automatic STM32 device detection (F1/F4/F7/G0 series)
- Support for multiple firmware formats (.hex, .bin)
- Single unified command-line interface
- Extensible architecture for supporting additional programmers
- Future: RTT logging and device testing

## Installation

```bash
pip install rhs-flashkit
```

## Usage

### Command Line

List connected programmers:
```bash
rhs-flash
# or specify programmer type
rhs-flash --programmer jlink
```

Flash a device with auto-detected programmer (uses first available JLink):
```bash
rhs-flash <firmware_file>
```

Flash with specific serial number:
```bash
rhs-flash <firmware_file> --serial <serial_number>
```

Flash with specific MCU:
```bash
rhs-flash <firmware_file> --mcu STM32F765ZG
```

Specify programmer explicitly:
```bash
rhs-flash <firmware_file> --programmer jlink --serial 123456
```

Get help:
```bash
rhs-flash --help
```

### Python API

```python
from rhs_flashkit import (
    flash_device_by_usb, 
    auto_detect_device, 
    get_connected_devices,
    get_first_available_device,
    find_device_by_serial
)
import pylink

# List all connected JLink devices
devices = get_connected_devices('jlink')
for device in devices:
    print(f"JLink Serial: {device['serial']}")

# Get first available device
first_device = get_first_available_device('jlink')
if first_device:
    print(f"First device: {first_device['serial']}")

# Find specific device
device = find_device_by_serial(123456, 'jlink')

# Flash with auto-detected programmer (first available JLink)
flash_device_by_usb(fw_file="firmware.hex")

# Flash with specific serial number
flash_device_by_usb(serial=123456, fw_file="firmware.hex")

# Flash with specific MCU and programmer
flash_device_by_usb(serial=123456, fw_file="firmware.hex", mcu="STM32F765ZG", programmer="jlink")

# Or detect device manually
jlink = pylink.JLink()
jlink.open(serial_no=123456)
jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
mcu = auto_detect_device(jlink, verbose=True)
print(f"Detected: {mcu}")
jlink.close()
```

## Development

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Currently Supported

### Programmers
- JLink (via pylink-square)

### Devices
- STM32F1 series (Low/Medium/High/XL density, Connectivity line)
- STM32F4 series (F405/407/415/417, F427/429/437/439)
- STM32F7 series (F74x/75x, F76x/77x)
- STM32G0 series (G0x0, G0x1, G0Bx/G0Cx)

## Roadmap

### Planned Features

- **RTT Logging** - Real-Time Transfer logging support
  - Read logs from devices during runtime
  - Integration with testing framework
  
- **Device Testing** - Automated testing capabilities
  - Run tests on connected devices
  - Collect and analyze test results via RTT
  - Generate test reports
  
- **Additional Programmers**
  - ST-Link support
  - OpenOCD support
  - Custom programmer interfaces

## Extending with New Programmers

The library is organized into functional modules:

- `constants.py` - Programmer type constants
- `list_devices.py` - Device detection and listing functionality
- `flashing.py` - Flashing operations
- `jlink_device_detector.py` - STM32-specific device detection

To add support for a new programmer:

1. Add the programmer constant to `src/rhs_flashkit/constants.py`:
```python
PROGRAMMER_STLINK = "stlink"
SUPPORTED_PROGRAMMERS = [PROGRAMMER_JLINK, PROGRAMMER_STLINK]
```

2. Implement device listing in `src/rhs_flashkit/list_devices.py`:
```python
def _get_stlink_devices() -> List[Dict[str, Any]]:
    # Implementation here
    pass

# Update get_connected_devices() function to handle new programmer
```

3. Implement flashing function in `src/rhs_flashkit/flashing.py`:
```python
def _flash_with_stlink(serial: int, fw_file: str, mcu: str = None) -> None:
    # Implementation here
    pass

# Add case in flash_device_by_usb()
elif programmer_lower == PROGRAMMER_STLINK:
    _flash_with_stlink(serial, fw_file, mcu)
```

4. Update documentation and tests

## License

MIT
