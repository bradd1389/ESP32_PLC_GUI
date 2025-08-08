# Changelog

All notable changes to ESP32 PLC GUI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-07

### Added
- Initial release of ESP32 PLC GUI
- Flowchart-style visual programming interface
- Drag-and-drop logic blocks with multi-port system
- Auto-routed wire connections with rounded corners
- Copy/paste functionality for blocks and wires
- Professional PyQt6 user interface with dockable panels
- Complete project management (New, Open, Save, Save As)
- JSON-based project file format
- ESP32-S3-WROOM hardware integration and configuration
- Setup Dialog with comprehensive ESP32 settings
- Tags/Variables system with bidirectional synchronization
- GPIO configuration for 36 pins
- I/O management for digital/analog inputs and PWM outputs
- Register mapping system for ESP32 hardware
- WiFi configuration and management
- Professional UI styling with consistent color scheme
- Memory allocation support for 1024KB RAM (ESP32-S3)
- PWM-based analog output for ESP32-S3 compatibility

### Features
- **Core Editor**: Flowchart canvas with intelligent block placement
- **Block System**: Multi-input/output logic blocks with dynamic port assignment
- **Wire Routing**: Automatic wire routing with collision avoidance
- **Project Management**: Complete file operations with metadata
- **Hardware Integration**: ESP32-S3-WROOM specific configuration
- **Variable System**: Real-time tag and variable management
- **UI/UX**: Modern interface with highlighting fixes

### Documentation
- Comprehensive README with installation and usage guide
- Block Configuration documentation
- Tags and Variables guide
- Wire Segments implementation guide
- Setup Tags Integration documentation
- Contributing guidelines
- MIT License

### Technical Specifications
- **Target Hardware**: ESP32-S3-WROOM (1024KB RAM, 36 GPIO pins)
- **UI Framework**: PyQt6 
- **Python Version**: 3.11+
- **File Format**: JSON-based project files (.plc extension)
- **Communication**: Serial and WiFi support for ESP32

### Known Limitations
- MicroPython/Arduino code export (planned for v1.1.0)
- Real-time ESP32 debugging (in development)
- WebREPL integration (planned for v1.2.0)

## [Unreleased]

### Planned
- MicroPython code generation and export
- Arduino IDE compatible code export
- Real-time ESP32 communication and debugging
- Logic simulation environment
- WebREPL wireless programming support
- Advanced block library expansion
- Custom block creation tools
- Multi-board project support

---

### Legend
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes
