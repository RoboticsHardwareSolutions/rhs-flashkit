# rhs-flashkit

CI/CD toolkit for flashing and testing embedded devices.

## Features

- Flash embedded devices (currently supports JLink)
- List and detect connected programmers
- Automatic STM32 device detection (F1/F4/F7/G0 series)
- Support for multiple firmware formats (.hex, .bin)
- **Real-Time Transfer (RTT) support** - Connect to device RTT for real-time communication
- Single unified command-line interface
- Extensible architecture for supporting additional programmers

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

### RTT (Real-Time Transfer)

Connect to JLink RTT for real-time communication with the target device:

```bash
# Connect with auto-detection and read for 10 seconds
rhs-jlink-rtt

# Specify JLink serial number
rhs-jlink-rtt --serial 123456789

# Connect via IP address (no MCU needed)
rhs-jlink-rtt --ip 192.168.1.100

# Specify MCU explicitly
rhs-jlink-rtt --mcu STM32F765ZG

# Read indefinitely until Ctrl+C
rhs-jlink-rtt -t 0

# Send message after connection
rhs-jlink-rtt --msg "hello\n"

# Send message after custom delay
rhs-jlink-rtt --msg "test" --msg-timeout 2.0

# Connect without resetting target
rhs-jlink-rtt --no-reset

# Verbose output
rhs-jlink-rtt -v
```

Get RTT help:
```bash
rhs-jlink-rtt --help
```

### Python API

#### Flashing

```python
from rhs_flashkit import JLinkProgrammer

# Create programmer instance (auto-detect serial)
prog = JLinkProgrammer()

# Or specify serial number
prog = JLinkProgrammer(serial=123456789)

# Flash firmware (auto-detect MCU)
prog.flash("firmware.hex")

# Flash with specific MCU
prog.flash("firmware.hex", mcu="STM32F765ZG")

# Flash without verification
prog.flash("firmware.hex", do_verify=False)

# Flash without reset
prog.flash("firmware.hex", reset=False)
```

#### RTT Communication

```python
from rhs_flashkit import JLinkProgrammer
import time

# Create programmer
prog = JLinkProgrammer(serial=123456789)

try:
    # Connect to target
    prog._connect_target(mcu="STM32F765ZG")
    
    # Reset device (optional)
    prog.reset(halt=False)
    time.sleep(0.5)
    
    # Start RTT
    prog.start_rtt(delay=1.0)
    
    # Send data
    prog.rtt_write(b"Hello, device!\n")
    
    # Read data
    data = prog.rtt_read(max_bytes=4096)
    if data:
        print(data.decode('utf-8', errors='replace'))
    
    # Stop RTT
    prog.stop_rtt()
    
finally:
    # Disconnect
    prog._disconnect_target()
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
