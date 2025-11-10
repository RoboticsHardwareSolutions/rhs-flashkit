# RHS FlashKit - Roadmap

## Vision

RHS FlashKit is a comprehensive toolkit for embedded device development, testing, and deployment. Our goal is to provide a unified command-line interface for all common operations with embedded devices.

## Current State (v0.1.0)

### ✅ Implemented
- Device flashing via JLink
- Automatic device detection (STM32 F1/F4/F7/G0)
- Device listing and enumeration
- Support for .hex and .bin firmware formats
- Auto-detection of first available programmer
- Optional serial number specification

### 🎯 Command Structure
```bash
rhs-flash list              # List devices
rhs-flash firmware.hex      # Flash firmware
```

## Phase 1: RTT Logging (v0.2.0)

### Features
- **RTT Reader** - Read Real-Time Transfer logs from devices
  ```bash
  rhs-rtt                    # Start RTT logging
  rhs-rtt --serial 123456    # RTT from specific device
  rhs-rtt --output log.txt   # Save to file
  ```

- **RTT API**
  ```python
  from rhs_flashkit.rtt import start_rtt, read_rtt
  
  # Start RTT session
  with start_rtt(serial=123456) as rtt:
      for line in rtt:
          print(line)
  ```

- **Multi-channel support** - Read from multiple RTT channels
- **Filtering** - Filter logs by level/pattern
- **Timestamps** - Add timestamps to log entries

### Technical Implementation
- Use pylink RTT capabilities
- Buffered reading for performance
- Thread-safe operation
- Configurable buffer sizes

## Phase 2: Device Testing (v0.3.0)

### Features
- **Test Runner** - Execute tests on connected devices
  ```bash
  rhs-test                   # Run all tests
  rhs-test --suite unit      # Run specific test suite
  rhs-test --report junit    # Generate JUnit report
  ```

- **Test Framework Integration**
  - Read test results via RTT
  - Parse structured test output
  - Generate test reports (JUnit, HTML, JSON)

- **CI/CD Integration**
  - Exit codes for CI systems
  - JSON output for parsing
  - Test result artifacts

- **Testing API**
  ```python
  from rhs_flashkit.test import run_tests
  
  results = run_tests(
      serial=123456,
      suite='unit',
      timeout=60
  )
  
  print(f"Tests: {results.total}")
  print(f"Passed: {results.passed}")
  print(f"Failed: {results.failed}")
  ```

### Test Protocol
- Define standard test output format over RTT
- Support for test discovery
- Parallel test execution on multiple devices
- Test coverage reporting

## Phase 3: Additional Programmers (v0.4.0)

### ST-Link Support
```bash
rhs-flash firmware.hex --programmer stlink
```

### OpenOCD Support
```bash
rhs-flash firmware.hex --programmer openocd --config stm32f4.cfg
```

### Custom Programmer Interface
- Plugin architecture for custom programmers
- Standard programmer API
- Configuration file support

## Phase 4: Advanced Features (v0.5.0+)

### Device Management
- **Device Profiles** - Save and load device configurations
- **Batch Operations** - Flash multiple devices
- **Device Discovery** - Scan network for programmers

### Debugging Support
- **GDB Integration** - Start debug sessions
- **Breakpoint Management** - Set/remove breakpoints via CLI
- **Memory Operations** - Read/write memory

### Performance Optimization
- **Parallel Flashing** - Flash multiple devices simultaneously
- **Delta Updates** - Flash only changed sectors
- **Caching** - Cache device info for faster operations

### Web Interface (Optional)
- Dashboard for device monitoring
- Real-time RTT log viewer
- Test result visualization
- Remote device management

## Integration Goals

### CI/CD Platforms
- GitHub Actions integration
- GitLab CI integration
- Jenkins plugins
- Azure DevOps tasks

### IDEs and Tools
- VS Code extension
- CLion integration
- PlatformIO support

### Monitoring and Logging
- Prometheus metrics
- Grafana dashboards
- ELK stack integration

## Command Structure Evolution

```
rhs-flash <firmware>        # Flash device
rhs-flash list              # List devices

rhs-rtt                     # Start RTT logging (v0.2.0)
rhs-rtt --follow            # Follow mode
rhs-rtt --save log.txt      # Save to file

rhs-test                    # Run tests (v0.3.0)
rhs-test --suite <name>     # Run specific suite
rhs-test --report <format>  # Generate report

rhs-debug                   # Debug session (v0.5.0+)
rhs-device info             # Device information
rhs-device reset            # Reset device
```

## Module Structure Evolution

```
rhs_flashkit/
├── flash/              # Flashing operations (current)
│   ├── jlink.py
│   ├── stlink.py      # Phase 3
│   └── openocd.py     # Phase 3
├── rtt/               # RTT logging (Phase 1)
│   ├── reader.py
│   ├── parser.py
│   └── writer.py
├── test/              # Device testing (Phase 2)
│   ├── runner.py
│   ├── parser.py
│   └── reporter.py
├── debug/             # Debugging (Phase 4)
│   ├── gdb.py
│   └── breakpoints.py
└── devices/           # Device management (current)
    ├── detection.py
    └── profiles.py
```

## Contributing

We welcome contributions! Priority areas:
1. RTT logging implementation
2. Test framework integration
3. Additional programmer support
4. Documentation and examples

## Timeline

- **v0.1.0** - Q4 2025 (Current)
- **v0.2.0** - Q1 2026 (RTT Logging)
- **v0.3.0** - Q2 2026 (Device Testing)
- **v0.4.0** - Q3 2026 (Additional Programmers)
- **v0.5.0** - Q4 2026 (Advanced Features)

## Feedback

Your feedback is important! Please open issues on GitHub for:
- Feature requests
- Bug reports
- Use case discussions
- Integration ideas
