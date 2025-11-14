"""Tests for device listing functionality via Programmer classes."""

import pytest
from rhs_flashkit import JLinkProgrammer


def test_get_connected_devices_jlink():
    """Test getting connected JLink devices."""
    # This will return empty list if no devices connected, which is fine for testing
    devices = JLinkProgrammer.get_connected_devices()
    assert isinstance(devices, list)
    
    # If devices found, check structure
    if devices:
        for device in devices:
            assert 'serial' in device
            assert 'type' in device
            assert device['type'] == 'jlink'


def test_get_first_available_device():
    """Test getting first available device."""
    device = JLinkProgrammer.get_first_available_device()
    
    # If device found, check structure
    if device:
        assert 'serial' in device
        assert 'type' in device


def test_find_device_by_serial_not_found():
    """Test finding device that doesn't exist."""
    # Use non-existent serial
    device = JLinkProgrammer.find_device_by_serial(999999999)
    assert device is None
