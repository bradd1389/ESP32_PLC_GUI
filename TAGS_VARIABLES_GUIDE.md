# ESP32 PLC Tags/Variables System Guide

## 🏗️ **System Architecture Overview**

The enhanced Tags/Variables system provides comprehensive ESP32 hardware integration with three distinct tag categories:

### **1. Physical I/O Tags**
- **Direct GPIO Mapping**: Real-time hardware pin control
- **Support for**: Digital I/O, Analog I/O, PWM outputs
- **Auto-Configuration**: Based on ESP32 pin capabilities from `esp32_config.json`
- **Hardware Features**: Interrupt support, debouncing, pull-up/pull-down configuration

### **2. Hardware Register Tags**  
- **Direct Register Access**: Low-level ESP32 register manipulation
- **Categories**: GPIO, ADC, Timer, System registers
- **Memory Mapped**: Direct hardware address access
- **Expert Mode**: For advanced users requiring hardware-level control

### **3. Software Variables**
- **Virtual Memory**: ESP32 RAM-based variables
- **Data Types**: BOOL, BYTE, INT, WORD, DWORD, FLOAT, STRING
- **Persistence**: Option for flash storage across power cycles
- **Memory Management**: Automatic ESP32 memory allocation

---

## 🎯 **Key Features**

### **Advanced Memory Management**
- **Automatic Allocation**: ESP32 RAM management with 320KB available space
- **Memory Mapping**: Visual memory usage display
- **Address Tracking**: Physical address assignment for all variables
- **Collision Prevention**: Prevents memory overlaps and conflicts

### **Physical I/O Integration**
- **Quick Add Buttons**: Fast creation of common I/O types
- **GPIO Pin Assignment**: Automatic pin configuration based on capabilities
- **Hardware Validation**: Ensures pins support requested I/O types
- **Real-time Status**: Live monitoring of physical pin states

### **Professional Tag Organization**
- **Tree Structure**: Hierarchical organization by tag type
- **Tabbed Interface**: Separate tabs for each tag category
- **Bulk Operations**: Import/export tag configurations
- **Search & Filter**: Quick tag location and management

### **ESP32 Hardware Awareness**
- **Pin Capability Detection**: Automatic detection of ADC, PWM, interrupt capabilities
- **Register Database**: Complete ESP32 register definitions
- **Memory Regions**: Proper RAM/Flash memory allocation
- **Hardware Limits**: Enforced GPIO and memory usage limits

---

## 📋 **User Interface Guide**

### **Opening the Tags Manager**
1. Click the **"Tags"** button in the main menu bar
2. Large resizable dialog opens (1200x800 pixels)
3. Three main sections: Tag Tree, Quick Add, and Detailed Editor

### **Tag Tree (Left Panel)**
```
📁 Physical I/O
  ├── DI_00 (Digital Input) - GPIO_2
  ├── DO_00 (Digital Output) - GPIO_4
  └── AI_00 (Analog Input) - ADC1_CH0

📁 Hardware Registers  
  ├── REG_GPIO_OUT - 0x3FF44004
  └── REG_ADC1_DATA - 0x3FF48800

📁 Software Variables
  ├── PLC_STATUS (BOOL) - 0x3FFAE000
  ├── CYCLE_COUNT (DWORD) - 0x3FFAE004
  └── TEMP_SETPOINT (FLOAT) - 0x3FFAE008
```

### **Quick Add Section**
- **+ Digital Input**: Creates new digital input tag
- **+ Digital Output**: Creates new digital output tag  
- **+ Analog Input**: Creates new analog input tag
- **+ Analog Output**: Creates new analog output tag (if DAC available)
- **+ PWM Output**: Creates new PWM output tag

### **Detailed Editor Tabs**

#### **Physical I/O Tab**
| Column | Description |
|--------|-------------|
| Tag Name | User-friendly variable name |
| I/O Type | Digital/Analog Input/Output, PWM |
| GPIO Pin | Physical ESP32 pin assignment |
| Physical Address | Hardware register address |
| Data Type | BOOL, BYTE, INT, WORD |
| Initial Value | Startup value |
| Description | User documentation |
| Enabled | Include in project |

#### **Hardware Registers Tab**
| Column | Description |
|--------|-------------|
| Tag Name | Register variable name |
| Register Name | Official ESP32 register name |
| Physical Address | Memory-mapped address |
| Data Type | Register data width |
| Access | Read/Write permissions |
| Description | Register functionality |
| Enabled | Include in project |

#### **Software Variables Tab**
| Column | Description |
|--------|-------------|
| Tag Name | Variable identifier |
| Data Type | BOOL, BYTE, INT, WORD, DWORD, FLOAT, STRING |
| Initial Value | Startup value |
| Memory Address | Allocated RAM address |
| Persistent | Save to flash memory |
| Array Size | Number of array elements |
| Min/Max Value | Value validation limits |
| Description | Variable purpose |

#### **Memory Overview Tab**
- **RAM Usage**: Current/Total available (320KB)
- **Flash Usage**: Persistent variable storage
- **GPIO Usage**: Pin allocation status
- **Memory Map**: Visual address allocation display

---

## 🔧 **Configuration Management**

### **Save/Load Integration**
- **Project Files**: Tags automatically included in `.plc` project files
- **Standalone Config**: Save/load tag configuration independently
- **Import/Export**: Share tag configurations between projects
- **Version Control**: Track configuration changes

### **Validation System**
- **Name Validation**: PLC-compliant naming conventions
- **Duplicate Detection**: Prevents conflicting tag names
- **Memory Validation**: Ensures sufficient ESP32 resources
- **Hardware Validation**: Confirms pin availability and capabilities

### **ESP32 Configuration Integration**
- **Pin Definitions**: Loaded from `esp32_config.json`
- **Register Database**: Complete ESP32 register mappings
- **Capability Matrix**: Pin-specific feature availability
- **Default Settings**: Pre-configured common I/O scenarios

---

## 📊 **Memory Management Details**

### **ESP32 Memory Layout**
```
📦 ESP32 Memory Map
├── 0x3FFAE000 - 0x3FFFFFFF: Available RAM (320KB)
├── 0x400000   - 0x800000:   Flash Memory (4MB)
└── GPIO Registers:          Hardware mapped I/O
```

### **Automatic Allocation**
- **Sequential Assignment**: Variables allocated in memory order
- **Type-Aware Sizing**: Proper byte alignment for data types
- **Collision Avoidance**: Prevents memory conflicts
- **Efficient Packing**: Minimizes memory fragmentation

### **Persistent Storage**
- **Flash Allocation**: Non-volatile storage for persistent variables
- **Retention Settings**: Configure power-loss data retention
- **Wear Leveling**: ESP32 flash management integration
- **Backup/Recovery**: Configuration restore capabilities

---

## 🎛️ **Advanced Features**

### **Real-Time Monitoring**
- **Live Values**: Display current tag values during runtime
- **Status Indicators**: Communication and error status
- **Historical Data**: Tag value change logging
- **Alarm Integration**: Configurable limit monitoring

### **Communication Integration**
- **Modbus Support**: Industrial protocol compatibility
- **Network Tags**: Remote device variable access
- **Serial Communication**: ESP32 UART tag mapping
- **Wireless Integration**: WiFi/Bluetooth tag synchronization

### **Code Generation**
- **ESP32 Headers**: Automatic C/C++ tag definitions
- **Memory Maps**: Linker script generation
- **Initialization Code**: Startup configuration routines
- **Runtime Libraries**: Tag access and management functions

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Memory Allocation Errors**
- **Symptom**: "Insufficient RAM for variable allocation"
- **Solution**: Reduce number of variables or use smaller data types
- **Prevention**: Monitor memory usage in Memory Overview tab

#### **GPIO Pin Conflicts**
- **Symptom**: Pin assignment failures
- **Solution**: Check pin capabilities and existing assignments
- **Prevention**: Use Quick Add buttons for automatic pin selection

#### **Tag Name Validation Errors**
- **Symptom**: Invalid tag name errors
- **Solution**: Use alphanumeric characters and underscores only
- **Prevention**: Follow PLC naming conventions (start with letter/underscore)

### **Performance Optimization**
- **Minimize String Variables**: Use fixed-length alternatives
- **Efficient Data Types**: Choose smallest appropriate type
- **Reduce Persistent Variables**: Limit flash write operations
- **Optimize Scan Rates**: Balance performance with responsiveness

---

## 📈 **Best Practices**

### **Tag Organization**
1. **Consistent Naming**: Use prefixes (DI_, DO_, AI_, AO_, VAR_)
2. **Logical Grouping**: Group related tags together
3. **Clear Descriptions**: Document tag purpose and usage
4. **Version Control**: Track configuration changes

### **Memory Management**
1. **Plan Allocation**: Design memory layout before implementation
2. **Monitor Usage**: Regularly check memory consumption
3. **Optimize Types**: Use appropriate data types for value ranges
4. **Backup Configs**: Save tag configurations regularly

### **Hardware Integration**
1. **Verify Capabilities**: Check pin functions before assignment
2. **Test Configurations**: Validate I/O operations
3. **Document Wiring**: Maintain hardware connection records
4. **Plan Expansion**: Reserve pins for future requirements

---

## 🚀 **Getting Started Checklist**

### **Initial Setup**
- [ ] Open Tags Manager from main menu
- [ ] Review default ESP32 pin configuration
- [ ] Add required Digital Inputs using Quick Add
- [ ] Add required Digital Outputs using Quick Add
- [ ] Configure Analog Inputs if needed
- [ ] Create Software Variables for logic operations

### **Configuration**
- [ ] Assign meaningful tag names
- [ ] Set appropriate data types
- [ ] Configure initial values
- [ ] Add descriptions for documentation
- [ ] Enable required tags
- [ ] Validate configuration

### **Testing**
- [ ] Save project with tag configuration
- [ ] Test tag validation
- [ ] Verify memory allocation
- [ ] Check GPIO pin assignments
- [ ] Export configuration for backup

### **Implementation**
- [ ] Generate ESP32 code
- [ ] Upload to ESP32 device
- [ ] Test physical I/O operations
- [ ] Verify software variable behavior
- [ ] Monitor system performance

---

## 🔗 **Related Documentation**

- **[ESP32_CONFIG_README.md](ESP32_CONFIG_README.md)**: ESP32 hardware configuration details
- **[SETUP_DIALOG_GUIDE.md](SETUP_DIALOG_GUIDE.md)**: Communication setup procedures
- **[PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md)**: Complete development workflow
- **[WIRE_SEGMENTS_GUIDE.md](WIRE_SEGMENTS_GUIDE.md)**: Logic block connections

---

*This enhanced Tags/Variables system provides professional-grade ESP32 integration for industrial PLC applications. The system automatically manages hardware resources while providing comprehensive tag organization and memory management capabilities.*
