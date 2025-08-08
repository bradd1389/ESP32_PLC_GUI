# ESP32 PLC GUI

A professional flowchart-style PLC programming environment for ESP32-S3 microcontrollers. This application provides an intuitive visual programming interface with drag-and-drop logic blocks, auto-routed wiring, and comprehensive project management capabilities.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## Features

### ✅ Core Functionality
- **Visual Programming**: Drag-and-drop logic blocks with flowchart-style programming
- **Auto-Routed Wiring**: Intelligent wire routing with rounded corners and automatic reconnection
- **Multi-Port Logic Blocks**: Support for complex logic with multiple inputs and outputs
- **Copy/Paste Operations**: Full block and wire duplication with position offsetting
- **Project Management**: Complete file operations (New, Open, Save, Save As) with JSON-based storage
- **Professional UI**: Modern PyQt6 interface with dockable panels and consistent styling

### 🔧 Hardware Integration
- **ESP32-S3-WROOM Support**: Optimized for ESP32-S3 with 1024KB RAM allocation
- **GPIO Configuration**: 36 configurable GPIO pins with hardware mapping
- **I/O Management**: Digital/Analog inputs, PWM outputs, and peripheral configuration
- **Register Mapping**: Complete ESP32 register definition and tag assignment system
- **WiFi Configuration**: Wireless communication setup and management

### 📊 Development Tools
- **Setup Dialog**: Comprehensive ESP32 configuration with real-time testing
- **Tags/Variables System**: Bidirectional data synchronization with hardware registers
- **Project Panel**: Hierarchical project organization and management
- **Variable Panel**: Real-time variable monitoring and configuration

## Installation

### Prerequisites
- Python 3.11 or higher
- PyQt6
- ESP32-S3 development board (optional for simulation)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/Bradd1389/ESP32_PLC_GUI.git
cd ESP32_PLC_GUI
```

2. Install required dependencies:
```bash
pip install PyQt6 pyserial
```

3. Run the application:
```bash
python Main.py
```

## Usage

### Quick Start
1. **Launch the Application**: Run `python Main.py`
2. **Create a New Project**: File → New Project
3. **Configure Hardware**: Tools → Setup Dialog to configure your ESP32-S3
4. **Design Logic**: Drag blocks from the toolbox to the canvas
5. **Connect Blocks**: Click on ports to create auto-routed wires
6. **Save Project**: File → Save Project

### Basic Workflow
1. **Setup Hardware Configuration**
   - Open Setup Dialog from the Tools menu
   - Configure ESP32-S3 settings, GPIO pins, and communication
   - Test connection to your development board

2. **Create Logic Flowchart**
   - Drag logic blocks from the toolbox
   - Connect blocks using the port system
   - Use copy/paste for rapid development

3. **Configure Variables**
   - Define tags and variables in the Variables panel
   - Map hardware registers to software variables
   - Monitor real-time values during debugging

4. **Export and Deploy**
   - Export to MicroPython or Arduino code (coming soon)
   - Upload directly to ESP32-S3 via serial connection

## Project Structure

```
ESP32_PLC_GUI/
├── Main.py                 # Application entry point
├── editor/                 # Core editor components
│   ├── flowchart_canvas.py # Main drawing canvas
│   ├── draggable_block.py  # Logic block implementation
│   ├── auto_routed_wire.py # Wire routing system
│   ├── toolbox.py          # Block toolbox
│   ├── setup_dialog.py     # Hardware configuration
│   ├── project_panel.py    # Project management
│   ├── variable_panel.py   # Variable/tags management
│   └── logic_exporter.py   # Code generation (future)
├── serial/                 # ESP32 communication
│   └── uploader.py         # Serial upload utilities
├── templates/              # Configuration templates
│   ├── esp32_config.json   # ESP32-S3 hardware definitions
│   ├── project_config.json # Project template
│   └── script_template.py  # Generated code template
└── docs/                   # Documentation
    ├── BLOCK_CONFIG_README.md
    ├── TAGS_VARIABLES_GUIDE.md
    └── WIRE_SEGMENTS_GUIDE.md
```

## Development Status

### ✅ Completed
- Multi-input/output logic block system
- Auto-routed wire connections with dynamic updating
- Copy/paste functionality for blocks and wires
- JSON-based project file format
- ESP32-S3-WROOM hardware integration
- Professional UI with consistent styling
- Setup ↔ Tags bidirectional synchronization
- PWM-based analog output for ESP32-S3 compatibility

### 🚧 In Progress
- MicroPython/Arduino code export
- Real-time ESP32 communication and debugging
- Advanced logic block library expansion

### 📋 Planned
- WebREPL integration for wireless programming
- Logic simulation and testing environment
- Custom block creation tools
- Multi-board project support

## Hardware Requirements

### Supported Boards
- **ESP32-S3-WROOM** (Primary target)
  - 1024KB RAM
  - 36 configurable GPIO pins
  - WiFi/Bluetooth connectivity
  - PWM output channels

### Minimum System Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB available space
- **Display**: 1280x720 minimum resolution

## Contributing

We welcome contributions! Please see our [contribution guidelines](CONTRIBUTING.md) for details on:
- Code style and conventions
- Testing procedures
- Pull request process
- Issue reporting

## Documentation

For detailed documentation, see:
- [Block Configuration Guide](BLOCK_CONFIG_README.md)
- [Tags and Variables Guide](TAGS_VARIABLES_GUIDE.md)
- [Wire Segments Guide](WIRE_SEGMENTS_GUIDE.md)
- [Setup Tags Integration](SETUP_TAGS_INTEGRATION_GUIDE.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs and feature requests on [GitHub Issues](https://github.com/Bradd1389/ESP32_PLC_GUI/issues)
- **Discussions**: Join the community discussions for help and feedback
- **Email**: Contact the maintainer at [your-email@domain.com]

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) for the user interface
- Designed for [ESP32-S3](https://www.espressif.com/en/products/socs/esp32-s3) microcontrollers
- Inspired by industrial PLC programming environments