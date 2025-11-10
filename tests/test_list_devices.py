"""Tests for list_devices module."""

import pytest
from rhs_flashkit.list_devices import (
    get_connected_devices,
    get_first_available_device,
    find_device_by_serial,
)


def test_get_connected_devices_jlink():
    """Test getting connected JLink devices."""
    # This will return empty list if no devices connected, which is fine for testing
    devices = get_connected_devices('jlink')
    assert isinstance(devices, list)
    
    # If devices found, check structure
    if devices:
        for device in devices:
            assert 'serial' in device
            assert 'type' in device
            assert device['type'] == 'jlink'


def test_get_first_available_device():
    """Test getting first available device."""
    device = get_first_available_device('jlink')
    
    # If device found, check structure
    if device:
        assert 'serial' in device
        assert 'type' in device


def test_find_device_by_serial_not_found():
    """Test finding device that doesn't exist."""
    # Use non-existent serial
    device = find_device_by_serial(999999999, 'jlink')
    assert device is None


def test_unsupported_programmer():
    """Test that unsupported programmer raises error."""
    with pytest.raises(ValueError, match="Unsupported programmer"):
        get_connected_devices('unsupported')
