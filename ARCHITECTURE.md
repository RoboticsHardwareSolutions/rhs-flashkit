# Architecture

This document describes the internal architecture of rhs-flashkit.

## Module Organization

The library is organized into functional modules:

### Core Modules

- **`constants.py`** - Global constants and configuration
  - Programmer type constants (PROGRAMMER_JLINK, etc.)
  - List of supported programmers
  - Default values

- **`list_devices.py`** - Device detection and enumeration
  - `get_connected_devices()` - Get all connected devices
  - `get_first_available_device()` - Get first available device
  - `find_device_by_serial()` - Find specific device by serial
  - `print_connected_devices()` - Print device information
  - Private functions for each programmer type (e.g., `_get_jlink_devices()`)

- **`flashing.py`** - Flashing operations
  - `flash_device_by_usb()` - Main flashing function
  - Private functions for each programmer type (e.g., `_flash_with_jlink()`)
  - CLI entry point in `main()`

- **`jlink_device_detector.py`** - STM32-specific device detection
  - `detect_stm32_device()` - Detect STM32 by reading DBGMCU_IDCODE
  - `auto_detect_device()` - Auto-detect and connect
  - `get_device_info()` - Get device info by ID
  - Device ID mapping for STM32 families

### CLI Modules

- **`flashing.py`** - Main CLI entry point
  - Command: `rhs-flash`
  - Supports subcommands: `list`/`l` to list devices
  - Main flashing functionality

## Data Flow

### Listing Devices

```
User calls get_connected_devices('jlink')
  ↓
list_devices.py → get_connected_devices()
  ↓
list_devices.py → _get_jlink_devices()
  ↓
Returns list of device dictionaries
```

### Flashing Device

```
User calls flash_device_by_usb(serial, fw_file, mcu, programmer)
  ↓
flashing.py → flash_device_by_usb()
  ↓
Validates programmer type
  ↓
Routes to programmer-specific function
  ↓
flashing.py → _flash_with_jlink()
  ↓
If serial is None:
  list_devices.py → get_first_available_device()
  ↓
If mcu is None:
  jlink_device_detector.py → auto_detect_device()
  ↓
Flash firmware
```

## Adding New Programmers

To add a new programmer (e.g., ST-Link):

1. **Add constant** in `constants.py`:
   ```python
   PROGRAMMER_STLINK = "stlink"
   SUPPORTED_PROGRAMMERS.append(PROGRAMMER_STLINK)
   ```

2. **Add device listing** in `list_devices.py`:
   ```python
   def _get_stlink_devices() -> List[Dict[str, Any]]:
       # Implementation
       pass
   
   # Update get_connected_devices() to handle PROGRAMMER_STLINK
   ```

3. **Add flashing** in `flashing.py`:
   ```python
   def _flash_with_stlink(serial: int, fw_file: str, mcu: str = None) -> None:
       # Implementation
       pass
   
   # Update flash_device_by_usb() to route to _flash_with_stlink()
   ```

4. **Add device detection** (if needed):
   - Create new module like `stlink_device_detector.py`
   - Implement device-specific detection logic

5. **Update tests and documentation**

## Design Principles

1. **Separation of Concerns**
   - Device listing is separate from flashing
   - CLI commands are separate from library code
   - Each programmer has its own private implementation functions

2. **Extensibility**
   - Easy to add new programmers
   - Private functions (`_function_name`) for internal implementation
   - Public API remains stable

3. **Consistency**
   - All device listing functions return same structure
   - All flashing functions accept same parameters
   - Error handling is consistent across modules

4. **Optional Parameters**
   - Serial number is optional (auto-detect first device)
   - MCU is optional (auto-detect if supported)
   - Programmer defaults to 'jlink'

## Public API

The main public API (exported from `__init__.py`):

```python
# Device management
get_connected_devices(programmer='jlink')
get_first_available_device(programmer='jlink')
find_device_by_serial(serial, programmer='jlink')
print_connected_devices(programmer='jlink')

# Flashing
flash_device_by_usb(serial=None, fw_file=None, mcu=None, programmer='jlink')

# STM32 detection
detect_stm32_device(jlink, verbose=True)
auto_detect_device(jlink, verbose=True)
get_device_info(dev_id)

# Constants
SUPPORTED_PROGRAMMERS
DEFAULT_PROGRAMMER
PROGRAMMER_JLINK
```

## CLI Commands

- `rhs-flash` - Main command (entry: `flashing.py:main()`)
  - `rhs-flash list` or `rhs-flash l` - List connected devices
  - `rhs-flash <firmware>` - Flash firmware
