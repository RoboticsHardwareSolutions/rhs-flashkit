# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-11-19

### Changed
- **Major API Refactoring**: Simplified to pure OOP design with minimal public API
- Renamed `flash_target()` → `flash()` - now automatically handles connection/disconnection
- Renamed `reset_target()` → `reset()` for cleaner API
- Made device enumeration and connection methods private (`_connect_target`, `_disconnect_target`)
- `flash()` method now accepts `reset` parameter (default: True) to control post-flash reset
- Enabled INFO and ERROR logging by default
- Removed `verbose` parameter from `detect_target()` - uses logger levels instead

### Removed
- Removed `flash_device_by_usb()` function - use `JLinkProgrammer.flash()` directly
- Removed `connect_target()` and `disconnect_target()` from public API
- Removed `get_target_mcu()` and `is_connected()` methods
- Removed `get_connected_devices()`, `print_connected_devices()`, and device finding methods
- Removed context manager support (`__enter__`/`__exit__`) - no longer needed with auto-disconnect
- Removed outdated documentation files (ARCHITECTURE.md, PROGRAMMER_API.md)

### Fixed
- Fixed STM32F1 series flashing issues by properly setting device name via `exec_command`
- Fixed MCU auto-detection by trying multiple Cortex-M cores (M7→M4→M3→M0)
- Fixed connection state checking to use proper target connection verification

### Improved
- Simplified API: only 5 public methods - `__init__`, `flash()`, `probe()`, `reset()`, `detect_target()`
- `flash()` now handles all connection logic internally
- Better error handling and logging throughout
- Cleaner code structure with consistent naming conventions

## [0.1.0] - 2025-11-10

### Added
- Initial release of rhs-flashkit
- JLink programmer support via pylink-square
- Automatic STM32 device detection (F1/F4/F7/G0 series)
- Flash firmware to embedded devices (.hex and .bin formats)
- Command-line interface with `rhs-flash` command
- List and detect connected JLink programmers
- Flash with auto-detected programmer (first available JLink)
- Flash with specific serial number
- Flash with specific MCU specification
- Python API for programmatic access:
  - `flash_device_by_usb()` - Flash devices with various options
  - `get_connected_devices()` - List all connected devices
  - `get_first_available_device()` - Get first available device
  - `find_device_by_serial()` - Find device by serial number
  - `auto_detect_device()` - Auto-detect STM32 devices
- Support for multiple STM32 series:
  - STM32F1 (Low/Medium/High/XL density, Connectivity line)
  - STM32F4 (F405/407/415/417, F427/429/437/439)
  - STM32F7 (F74x/75x, F76x/77x)
  - STM32G0 (G0x0, G0x1, G0Bx/G0Cx)
- Extensible architecture for adding new programmers
- Comprehensive documentation and examples

### Dependencies
- Python >= 3.8
- pylink-square >= 1.0.0

[0.1.1]: https://github.com/RoboticsHardwareSolutions/rhs-flashkit/releases/tag/v0.1.1
[0.1.0]: https://github.com/RoboticsHardwareSolutions/rhs-flashkit/releases/tag/v0.1.0
