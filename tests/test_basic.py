"""Basic tests for rhs-flashkit."""

from rhs_flashkit import __version__, get_device_info


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_get_device_info():
    """Test device info retrieval."""
    # Test known F7 device
    info = get_device_info(0x451)
    assert "STM32F76x/77x" in info['family']
    assert info['default_mcu'] == "STM32F765ZG"
    
    # Test unknown device
    info = get_device_info(0xFFF)
    assert "Unknown" in info['family']
