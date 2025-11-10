"""Tests for flashing module."""

import pytest
from rhs_flashkit.flashing import flash_device_by_usb


def test_unsupported_programmer():
    """Test that unsupported programmer raises error."""
    with pytest.raises(ValueError, match="Unsupported programmer"):
        flash_device_by_usb(123456, "test.hex", programmer="unsupported")


def test_jlink_programmer_accepted():
    """Test that jlink programmer is accepted as valid choice."""
    # This will fail at connection time (no real hardware), but should pass validation
    try:
        flash_device_by_usb(123456, "test.hex", programmer="jlink")
    except Exception as e:
        # We expect it to fail at hardware level, not at validation
        assert "Unsupported programmer" not in str(e)
