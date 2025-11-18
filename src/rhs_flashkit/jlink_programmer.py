"""
JLink Programmer Implementation

This module provides JLink programmer implementation based on the Programmer abstract class.
Uses pylink-square library for communication with SEGGER J-Link devices.
"""

import logging
import pylink
from typing import Optional, List, Dict, Any
from .programmer import Programmer, DBGMCU_IDCODE_ADDRESSES, DEVICE_ID_MAP, DEFAULT_MCU_MAP

# Configure default logging level for JLinkProgrammer
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')


class JLinkProgrammer(Programmer):
    """JLink programmer implementation."""

    def __init__(self, serial: Optional[int] = None):
        """
        Initialize JLink programmer.
        
        Args:
            serial: JLink serial number (optional, will auto-detect first available if not provided)
        """
        super().__init__(serial)
        self._jlink = pylink.JLink()
        self._mcu = None
        
        # If no serial specified, find first available device
        if serial is None:
            devices = self._get_available_devices()
            if not devices:
                raise RuntimeError("No JLink devices found. Please connect a JLink.")
            self._serial = devices[0]['serial']
            print(f"Auto-detected JLink with serial: {self._serial}")
        else:
            self._serial = serial
            print(f"JLink with serial {serial} is available")

    def flash(self, file_path: str, mcu: Optional[str] = None, do_verify: bool = True, reset: bool = True) -> bool:
        """
        Flash firmware to the device using JLink.
        Automatically connects to target if not already connected.
        
        Args:
            file_path: Path to firmware file (.hex or .bin)
            mcu: MCU name (optional, will auto-detect if not provided)
            do_verify: Whether to verify the flash operation
            reset: Whether to reset device after flashing (default: True)
            
        Returns:
            True if flash was successful, False otherwise
        """
        try:
            # Connect to target if not already connected
            if not self._jlink.opened():
                if not self._connect_target(mcu=mcu):
                    self.logger.error("Failed to connect to device")
                    return False
            
            self.logger.info(f"Flashing {file_path}...")
            
            # Halt the core before flashing
            if not self._jlink.halted():
                self._jlink.halt()
                self.logger.debug("Core halted for flashing")
            
            # Flash at STM32 default flash base address
            result = self._jlink.flash_file(file_path, 0x08000000)
            
            if result < 0:
                self.logger.error(f"Flash failed with result: {result}")
                return False
            
            self.logger.info(f"Flash successful: {result} bytes written")
            
            if do_verify:
                self.logger.info("Verifying flash...")
                # JLink flash_file already includes verification by default
            
            # Reset device if requested
            if reset:
                self.logger.info("Resetting device...")
                self.reset(halt=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Flash error: {e}")
            return False
        finally:
            # Disconnect after flashing
            self._disconnect_target()

    def probe(self) -> bool:
        """
        Probe/detect if JLink is connected and accessible.
        
        Returns:
            True if JLink is detected, False otherwise
        """
        try:
            if self._serial:
                # Check if specific serial exists
                emulators = pylink.JLink().connected_emulators()
                return any(emu.SerialNumber == self._serial for emu in emulators)
            else:
                # Check if any JLink is connected
                emulators = pylink.JLink().connected_emulators()
                return len(emulators) > 0
        except Exception as e:
            self.logger.error(f"Probe error: {e}")
            return False

    def _connect_target(self, mcu: Optional[str] = None) -> bool:
        """
        Connect to the target device via JLink (private method).
        
        Args:
            mcu: MCU name (optional, will auto-detect if not provided)
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Open JLink connection
            if self._serial:
                self.logger.info(f"Opening JLink with serial: {self._serial}")
                self._jlink.open(serial_no=self._serial)
            else:
                self.logger.info("Opening JLink (first available)")
                self._jlink.open()

            if not self._jlink.opened():
                self.logger.error("Failed to open JLink")
                return False

            # Set interface to SWD
            self._jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
            self.logger.debug("Interface set to SWD")

            # Connect to MCU
            if mcu:
                self.logger.info(f"Connecting to specified MCU: {mcu}")
                self._jlink.connect(mcu)
                self._mcu = mcu
            else:
                self.logger.info("Auto-detecting MCU...")
                detected_mcu = self.detect_target()
                
                if detected_mcu:
                    self.logger.info(f"Detected MCU: {detected_mcu}")
                    self._mcu = detected_mcu
                    # Disconnect and reconnect with proper device name for correct flash programming
                    if self._jlink.connected():
                        try:
                            # Set device and reconnect for proper configuration
                            self._jlink.exec_command(f"device = {detected_mcu}")
                            self.logger.debug(f"Set device to {detected_mcu}")
                        except Exception as e:
                            self.logger.warning(f"Could not set device: {e}, will use generic connection")
                else:
                    self.logger.warning("Could not auto-detect MCU, trying generic Cortex-M4")
                    self._mcu = "Cortex-M4"
                    self._jlink.connect(self._mcu)

            self.logger.info(f"Connected to {self._mcu}")
            return True

        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False

    def _disconnect_target(self):
        """Disconnect from the target device and close JLink (private method)."""
        if self._jlink.opened():
            self.logger.info("Disconnecting from device")
            self._jlink.close()
        self._mcu = None

    def reset(self, halt: bool = False):
        """
        Reset the target device.
        
        Args:
            halt: Whether to halt after reset
        """
        if not self._jlink.opened():
            self.logger.warning("Not connected, cannot reset")
            return

        try:
            self.logger.info(f"Resetting device (halt={halt})")
            self._jlink.reset(halt=halt)
        except Exception as e:
            self.logger.error(f"Reset error: {e}")

    @staticmethod
    def _get_available_devices() -> List[Dict[str, Any]]:
        """
        Get list of all available JLink devices (private method).
        
        Returns:
            List of device information dictionaries:
            - serial: Serial number
            - product: Product name (if available)
            - type: 'jlink'
        """
        try:
            jlink = pylink.JLink()
            emulators = jlink.connected_emulators()
            
            devices = []
            for emu in emulators:
                device_info = {
                    'serial': emu.SerialNumber,
                    'type': 'jlink'
                }
                if hasattr(emu, 'acProduct'):
                    device_info['product'] = emu.acProduct
                devices.append(device_info)
            
            if jlink.opened():
                jlink.close()
                
            return devices
        except Exception as e:
            print(f"Warning: Could not enumerate JLink devices: {e}")
            return []

    def read_target_memory(self, address: int, num_bytes: int) -> Optional[list]:
        """
        Read memory from target device.
        
        Args:
            address: Memory address to read from
            num_bytes: Number of bytes to read
            
        Returns:
            List of bytes or None on error
        """
        if not self._jlink.opened():
            self.logger.error("Not connected to device")
            return None

        try:
            return self._jlink.memory_read(address, num_bytes)
        except Exception as e:
            self.logger.error(f"Memory read error: {e}")
            return None

    def detect_target(self) -> Optional[str]:
        """
        Detect STM32 device by reading DBGMCU_IDCODE register.
        
        Tries to connect with different Cortex-M cores and read device ID.
            
        Returns:
            Device name like 'STM32F765ZG' or 'STM32F103RE', or None if detection failed
        """
        # Try to connect with different Cortex-M cores
        # Order: M7 -> M4 -> M3 -> M0 (from most complex to simplest, as modern MCUs are more common)
        connected_core = None
        
        for core in ['Cortex-M7', 'Cortex-M4', 'Cortex-M3', 'Cortex-M0']:
            try:
                self.logger.debug(f"Trying to connect with {core}...")
                self._jlink.connect(core, verbose=False)
                
                # Try to read IDCODE to verify connection works
                try:
                    test_read = self._jlink.memory_read32(0xE0042000, 1)[0]
                    if test_read != 0 and test_read != 0xFFFFFFFF:
                        connected_core = core
                        self.logger.info(f"Successfully connected with {core}")
                        break
                except:
                    pass  # Connection didn't work, try next core
                    
            except Exception as e:
                self.logger.debug(f"Failed to connect with {core}: {e}")
                continue
        
        if not connected_core:
            self.logger.error("Could not connect with any Cortex-M core")
            return None

        try:
            # Try to read device ID from different addresses
            idcode = 0
            found_addr = None
            
            for addr, desc in DBGMCU_IDCODE_ADDRESSES.items():
                try:
                    idcode = self._jlink.memory_read32(addr, 1)[0]
                    if idcode != 0 and idcode != 0xFFFFFFFF:
                        self.logger.info(f"✓ Read IDCODE from 0x{addr:08X} ({desc})")
                        found_addr = addr
                        break
                    else:
                        self.logger.debug(f"✗ Address 0x{addr:08X} returned invalid IDCODE (0x{idcode:08X}) - skipping {desc}")
                except Exception as e:
                    self.logger.debug(f"✗ Cannot read from 0x{addr:08X} ({desc}): {e}")
                    continue
            
            if idcode == 0 or idcode == 0xFFFFFFFF or found_addr is None:
                self.logger.error("Could not read valid IDCODE from any known address")
                return None
            
            # Extract device and revision IDs
            dev_id = (idcode >> 0) & 0xFFF
            rev_id = (idcode >> 16) & 0xFFFF
            
            self.logger.info(f"Detected Device ID: 0x{dev_id:03X}, Revision ID: 0x{rev_id:04X}")
            
            # Get device family name
            device_family = DEVICE_ID_MAP.get(dev_id, f"Unknown (0x{dev_id:03X})")
            self.logger.info(f"Device Family: {device_family}")
            
            # Get default MCU name for this device ID
            mcu_name = DEFAULT_MCU_MAP.get(dev_id)
            
            if mcu_name is None:
                # Return generic name based on family if no specific default
                mcu_name = device_family.replace(" ", "_")
            
            return mcu_name
            
        except Exception as e:
            self.logger.warning(f"Could not detect device automatically: {e}")
            return None
