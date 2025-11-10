# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.1.0]: https://github.com/RoboticsHardwareSolutions/rhs-flashkit/releases/tag/v0.1.0
