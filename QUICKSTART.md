# Quick Start Guide

## Development Setup

```bash
# 1. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
# venv\Scripts\activate  # On Windows

# 2. Install package in editable mode
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Usage

### CLI Command

After installation, the `rhs-flash` command is available:

```bash
# List connected programmers
rhs-flash
rhs-flash --programmer jlink

# Flash with auto-detected JLink (first available)
rhs-flash firmware.hex

# With specific serial number
rhs-flash firmware.hex --serial 123456789

# With specific MCU
rhs-flash firmware.hex --mcu STM32F765ZG

# Specify everything explicitly
rhs-flash firmware.hex --serial 123456789 --mcu STM32F765ZG --programmer jlink

# Get help
rhs-flash --help
```

### Python API

```python
from rhs_flashkit import flash_device_by_usb

# Flash device (auto-detect first available JLink)
flash_device_by_usb(fw_file="firmware.hex")

# Flash with specific serial number
flash_device_by_usb(serial=123456789, fw_file="firmware.hex")

# Flash with specific programmer
flash_device_by_usb(serial=123456789, fw_file="firmware.hex", programmer="jlink")
```

## Building Package

```bash
# Install build tool
pip install build

# Build package
python -m build

# Output will be in dist/
```

## Publishing to PyPI

```bash
# Install twine
pip install twine

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Or to main PyPI
twine upload dist/*
```

## Project Structure

```
rhs_flashkit/
├── src/rhs_flashkit/       # Main package code
│   ├── __init__.py         # Package API
│   ├── flashing.py         # Flashing functions
│   ├── list_devices.py     # Device detection
│   └── jlink_device_detector.py  # Device detector
├── tests/                   # Tests
├── examples/                # Usage examples
├── pyproject.toml          # Project configuration
└── README.md               # Documentation
```

## Before Publishing

In `pyproject.toml`:
1. Update `authors` - your name and email
2. Update `Homepage` and `Repository` - links to your repository
3. Update `description` if needed

## Dependencies

Main dependencies:
- `pylink-square` - for JLink support (more programmers coming soon)

Development dependencies:
- `pytest` - for testing
- `pytest-cov` - for code coverage
