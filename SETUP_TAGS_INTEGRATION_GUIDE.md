# Setup Dialog ↔ Tags/Variables Integration Guide

## 🔗 **Bidirectional Integration Overview**

The Setup Dialog and Tags/Variables system are now **fully integrated** for seamless ESP32 I/O management. This integration provides a unified workflow where changes in either system automatically sync with the other.

---

## 🎯 **Integration Features**

### **✅ Bidirectional Synchronization**
- **Setup → Tags**: Export I/O configuration from Setup to Tags system
- **Tags → Setup**: Import tag definitions into Setup I/O tables
- **Real-time Sync**: Automatic updates when changes are made in either system

### **✅ Unified I/O Management**
- **Physical GPIO Pins**: Consistent pin assignments between both systems
- **Tag Naming**: Standardized naming conventions (DI_XX, DO_XX, AI_XX)
- **Configuration Persistence**: Settings saved in both Setup and Tags formats

### **✅ Professional Workflow**
- **Data Validation**: Ensures consistency between systems
- **Conflict Resolution**: Prevents duplicate pin assignments
- **Status Monitoring**: Visual feedback on sync operations

---

## 🎛️ **How to Use Integration**

### **Step 1: Access Integration Controls**

1. **Open Setup Dialog**: Click "Setup" button in main menu
2. **Navigate to I/O Configuration Tab**: Second tab in Setup Dialog
3. **Find Integration Section**: Located at bottom of I/O Configuration tab

### **Step 2: Integration Controls**

The integration section contains three main buttons:

#### **← Import from Tags**
- **Purpose**: Loads I/O configuration from Tags/Variables system into Setup
- **Use Case**: When you've configured tags first and want to update Setup
- **Process**: 
  - Clears existing Setup I/O tables
  - Imports enabled Physical I/O tags
  - Populates Digital Input, Digital Output, and Analog Input tables
  - Updates pin assignments and configurations

#### **Export to Tags →**
- **Purpose**: Sends Setup I/O configuration to Tags/Variables system
- **Use Case**: When you've configured I/O in Setup and want to create tags
- **Process**:
  - Extracts I/O settings from Setup tables
  - Finds matching GPIO pins in Tags system
  - Enables and configures corresponding tags
  - Updates tag names and properties

#### **⟷ Synchronize**
- **Purpose**: Full bidirectional sync between both systems
- **Use Case**: Ensuring both systems have identical configurations
- **Process**:
  - Exports Setup → Tags
  - Imports Tags → Setup
  - Validates consistency
  - Reports any conflicts

### **Step 3: Monitor Integration Status**

The **Status label** shows real-time integration feedback:
- 🟢 **Green**: Successful operations
- 🔴 **Red**: Errors or failures
- 🔵 **Blue**: Synchronization complete

---

## 📊 **Integration Mapping**

### **Setup Dialog Tables → Tags System**

| Setup Table | Tag Category | Mapping |
|-------------|--------------|---------|
| **Digital Inputs** | Physical I/O Tags | GPIO pin → Digital Input tag |
| **Digital Outputs** | Physical I/O Tags | GPIO pin → Digital Output tag |
| **Analog Inputs** | Physical I/O Tags | GPIO pin → Analog Input tag |
| **Register Mapping** | Hardware Register Tags | Register address → Register tag |

### **Field Mapping Details**

#### **Digital Input Mapping**
```
Setup Table          →  Tags System
─────────────────────────────────────
Pin (e.g., "2")      →  GPIO Pin ("GPIO2")
Mode                 →  Pin Mode
Interrupt            →  Interrupt Mode
Tag Name             →  Tag Name
```

#### **Digital Output Mapping**
```
Setup Table          →  Tags System
─────────────────────────────────────
Pin (e.g., "4")      →  GPIO Pin ("GPIO4")
Mode                 →  Pin Mode
Initial State        →  Initial Value
Tag Name             →  Tag Name
```

#### **Analog Input Mapping**
```
Setup Table          →  Tags System
─────────────────────────────────────
Pin (e.g., "36")     →  GPIO Pin ("GPIO36")
Resolution           →  (Setup-specific)
Attenuation          →  (Setup-specific)
Tag Name             →  Tag Name
```

---

## 🔄 **Synchronization Workflow**

### **Typical Development Workflow**

#### **Approach 1: Setup-First Workflow**
1. **Configure I/O in Setup Dialog**
   - Set up Digital Inputs with interrupts and modes
   - Configure Digital Outputs with initial states
   - Define Analog Inputs with scaling
   
2. **Export to Tags**
   - Click "Export to Tags →" button
   - Tags system automatically creates corresponding tags
   - Physical I/O tags are enabled and configured

3. **Refine in Tags System**
   - Open Tags dialog for advanced configuration
   - Add software variables as needed
   - Configure memory allocation and persistence

#### **Approach 2: Tags-First Workflow**
1. **Design Tags System**
   - Use Quick Add buttons for rapid I/O creation
   - Configure physical addresses and data types
   - Set up software variables and arrays

2. **Import to Setup**
   - Click "← Import from Tags" button
   - Setup I/O tables populated automatically
   - Hardware-specific settings applied

3. **Finalize Hardware Settings**
   - Adjust ADC resolution and attenuation
   - Configure PWM frequencies
   - Set communication parameters

#### **Approach 3: Bidirectional Workflow**
1. **Start with either system**
2. **Make changes in both systems as needed**
3. **Use "⟷ Synchronize" regularly**
4. **Resolve any conflicts that arise**

---

## ⚠️ **Important Considerations**

### **Pin Assignment Rules**
- **One Pin, One Function**: Each GPIO pin can only have one assignment
- **Hardware Limitations**: Not all pins support all functions (ADC, PWM, etc.)
- **Reserved Pins**: Some pins are reserved for system functions

### **Data Consistency**
- **Tag Names**: Must follow PLC naming conventions
- **Pin Numbers**: Must match ESP32 hardware capabilities
- **Data Types**: Must be compatible between systems

### **Conflict Resolution**
- **Duplicate Pins**: Integration will warn about conflicts
- **Name Collisions**: Duplicate tag names are prevented
- **Type Mismatches**: Invalid configurations are flagged

---

## 🛠️ **Advanced Integration Features**

### **Real-Time Updates**
- **Automatic Sync**: Changes in Setup tables trigger tag updates
- **Change Detection**: Modified cells automatically propagate
- **Signal-Based**: Uses Qt signals for efficient communication

### **Configuration Validation**
- **Pin Capability Check**: Ensures pins support requested functions
- **Name Validation**: Enforces PLC naming standards
- **Memory Validation**: Checks ESP32 resource availability

### **Persistence Integration**
- **Project Files**: Both configurations saved together
- **Standalone Configs**: Tags can be exported independently
- **Version Control**: Track changes across both systems

---

## 🎯 **Best Practices**

### **Development Workflow**
1. **Plan Your I/O**: Document physical connections first
2. **Choose Your Starting Point**: Use Setup for hardware, Tags for logic
3. **Sync Early and Often**: Regular synchronization prevents conflicts
4. **Validate Configurations**: Use validation tools before deployment

### **Naming Conventions**
- **Digital Inputs**: `DI_XX` (e.g., DI_00, DI_01)
- **Digital Outputs**: `DO_XX` (e.g., DO_00, DO_01)
- **Analog Inputs**: `AI_XX` (e.g., AI_00, AI_01)
- **Descriptive Names**: Use meaningful descriptions for documentation

### **Configuration Management**
- **Save Regularly**: Both systems auto-save with projects
- **Export Backups**: Create standalone tag configurations
- **Document Changes**: Use description fields for change tracking
- **Test Integration**: Verify sync operations before deployment

---

## 🔍 **Troubleshooting Integration**

### **Common Issues**

#### **Import/Export Failures**
- **Symptom**: Red status message, no data transfer
- **Causes**: Missing variable panel, invalid configurations
- **Solution**: Ensure Tags dialog has been opened at least once

#### **Pin Assignment Conflicts**
- **Symptom**: Warning messages about duplicate pins
- **Causes**: Same GPIO assigned to multiple functions
- **Solution**: Review pin assignments, use different pins

#### **Tag Name Validation Errors**
- **Symptom**: Invalid tag name messages
- **Causes**: Non-compliant naming (spaces, special characters)
- **Solution**: Use alphanumeric characters and underscores only

#### **Sync Status Shows Errors**
- **Symptom**: Red status with error descriptions
- **Causes**: Various validation or system errors
- **Solution**: Check error message, resolve underlying issue

### **Debugging Tips**
1. **Check Status Messages**: Integration status provides detailed feedback
2. **Validate Individually**: Test import and export separately
3. **Review Pin Capabilities**: Ensure pins support requested functions
4. **Clear and Restart**: Clear configurations and start fresh if needed

---

## 📈 **Benefits of Integration**

### **Efficiency Gains**
- **No Duplicate Work**: Configure once, use everywhere
- **Reduced Errors**: Automatic validation prevents mistakes
- **Faster Development**: Quick synchronization speeds workflow

### **Consistency Assurance**
- **Unified Configuration**: Single source of truth for I/O
- **Automatic Validation**: Built-in conflict detection
- **Professional Standards**: Enforced naming conventions

### **Professional Workflow**
- **Industrial Standards**: Follows PLC development practices
- **Team Collaboration**: Consistent configurations across team
- **Documentation**: Automatic documentation generation

---

This integration represents a **professional-grade solution** that bridges hardware configuration and software logic programming, providing the unified workflow essential for industrial PLC development! 🎯

---

## 🔗 **Related Documentation**

- **[TAGS_VARIABLES_GUIDE.md](TAGS_VARIABLES_GUIDE.md)**: Complete Tags/Variables system guide
- **[SETUP_DIALOG_GUIDE.md](#)**: Comprehensive Setup Dialog documentation (to be created)
- **[ESP32_CONFIG_README.md](#)**: ESP32 hardware configuration details
- **[PROJECT_CHECKLIST.md](PROJECT_CHECKLIST.md)**: Development workflow checklist
