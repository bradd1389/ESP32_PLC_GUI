import json
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QComboBox, QCheckBox, QPushButton, 
                            QSpinBox, QLineEdit, QTabWidget, QGroupBox, QFormLayout,
                            QLabel, QTextEdit, QMessageBox, QHeaderView, QSplitter,
                            QTreeWidget, QTreeWidgetItem, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# Handle imports for both direct execution and module import
try:
    from .tag_model import Tag, PhysicalIOTag, RegisterTag, SoftwareTag
except ImportError:
    try:
        from tag_model import Tag, PhysicalIOTag, RegisterTag, SoftwareTag
    except ImportError:
        # If tag_model doesn't exist, create basic classes for compatibility
        from typing import TYPE_CHECKING
        
        if TYPE_CHECKING:
            # For type checking, use Any to avoid conflicts
            from typing import Any
            Tag = Any
            PhysicalIOTag = Any
            RegisterTag = Any
            SoftwareTag = Any
        else:
            # Runtime fallback classes
            class Tag:
                def __init__(self, name: str = "", tag_type: str = "", **kwargs):
                    self.name = name
                    self.tag_type = tag_type
                    for key, value in kwargs.items():
                        setattr(self, key, value)
            
            class PhysicalIOTag(Tag):
                def __init__(self, name: str = "", tag_type: str = "", gpio_pin: str = "", **kwargs):
                    super().__init__(name, tag_type, **kwargs)
                    self.gpio_pin = gpio_pin
            
            class RegisterTag(Tag):
                def __init__(self, name: str = "", tag_type: str = "", register_address: str = "", **kwargs):
                    super().__init__(name, tag_type, **kwargs)
                    self.register_address = register_address
            
            class SoftwareTag(Tag):
                def __init__(self, name: str = "", tag_type: str = "", memory_address: str = "", **kwargs):
                    super().__init__(name, tag_type, **kwargs)
                    self.memory_address = memory_address

# Enhanced tag types with physical mapping
TAG_CATEGORIES = {
    "Physical I/O": {
        "Digital Input": {"type": "BOOL", "access": "R", "memory": "GPIO"},
        "Digital Output": {"type": "BOOL", "access": "RW", "memory": "GPIO"},
        "Analog Input": {"type": "INT", "access": "R", "memory": "ADC"},
        "Analog Output": {"type": "INT", "access": "RW", "memory": "PWM"},
        "PWM Output": {"type": "INT", "access": "RW", "memory": "PWM"}
    },
    "Hardware Registers": {
        "GPIO Register": {"type": "DWORD", "access": "RW", "memory": "REG"},
        "ADC Register": {"type": "DWORD", "access": "R", "memory": "REG"},
        "Timer Register": {"type": "DWORD", "access": "RW", "memory": "REG"},
        "System Register": {"type": "DWORD", "access": "R", "memory": "REG"}
    },
    "Software Variables": {
        "Boolean": {"type": "BOOL", "access": "RW", "memory": "RAM"},
        "Byte": {"type": "BYTE", "access": "RW", "memory": "RAM"},
        "Integer": {"type": "INT", "access": "RW", "memory": "RAM"},
        "Word": {"type": "WORD", "access": "RW", "memory": "RAM"},
        "Double Word": {"type": "DWORD", "access": "RW", "memory": "RAM"},
        "Float": {"type": "FLOAT", "access": "RW", "memory": "RAM"},
        "String": {"type": "STRING", "access": "RW", "memory": "RAM"}
    }
}

class VariablePanel(QWidget):
    # Signal emitted when tags are modified
    tags_modified = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.tags = []
        self.esp32_config = self.load_esp32_config()
        self.memory_allocator = ESP32MemoryAllocator()
        
        # Configure proper styling to fix highlighting issues
        self.setup_styles()
        
        # Initialize layout
        self.init_ui()
        self.load_existing_tags()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side: Tag tree and quick add
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Tag tree for organization
        self.create_tag_tree(left_layout)
        
        # Quick add section
        self.create_quick_add_section(left_layout)
        
        splitter.addWidget(left_widget)
        
        # Right side: Detailed tag editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Create tabbed interface for different tag types
        self.create_tag_editor_tabs(right_layout)
        
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 500])
        
        # Bottom controls
        self.create_control_buttons(layout)

    def setup_styles(self):
        """Configure proper styling to fix highlighting and selection issues"""
        style = """
        QTableWidget {
            selection-background-color: #3daee9;
            selection-color: white;
            alternate-background-color: #f0f0f0;
            gridline-color: #d0d0d0;
        }
        
        QTableWidget::item:selected {
            background-color: #3daee9;
            color: white;
        }
        
        QTableWidget::item:hover {
            background-color: #e0f0ff;
            color: black;
        }
        
        QTreeWidget {
            selection-background-color: #3daee9;
            selection-color: white;
            alternate-background-color: #f0f0f0;
        }
        
        QTreeWidget::item:selected {
            background-color: #3daee9;
            color: white;
        }
        
        QTreeWidget::item:hover {
            background-color: #e0f0ff;
            color: black;
        }
        
        QComboBox {
            selection-background-color: #3daee9;
            selection-color: white;
        }
        
        QComboBox QAbstractItemView {
            selection-background-color: #3daee9;
            selection-color: white;
            background-color: white;
            color: black;
        }
        
        QComboBox QAbstractItemView::item:selected {
            background-color: #3daee9;
            color: white;
        }
        
        QComboBox QAbstractItemView::item:hover {
            background-color: #e0f0ff;
            color: black;
        }
        
        QLineEdit:focus {
            border: 2px solid #3daee9;
            background-color: white;
            color: black;
        }
        
        QTextEdit:focus {
            border: 2px solid #3daee9;
            background-color: white;
            color: black;
        }
        
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        
        QTabBar::tab:selected {
            background-color: #3daee9;
            color: white;
        }
        
        QTabBar::tab:hover {
            background-color: #e0f0ff;
            color: black;
        }
        """
        self.setStyleSheet(style)

    def create_tag_tree(self, layout):
        """Create organized tag tree view"""
        tree_group = QGroupBox("Tag Organization")
        tree_layout = QVBoxLayout(tree_group)
        
        self.tag_tree = QTreeWidget()
        self.tag_tree.setHeaderLabels(["Name", "Type", "Address", "Value"])
        self.tag_tree.itemSelectionChanged.connect(self.on_tag_selected)
        
        # Create category nodes
        self.physical_node = QTreeWidgetItem(["Physical I/O", "", "", ""])
        self.physical_node.setFont(0, QFont("Arial", 10, QFont.Weight.Bold))
        self.tag_tree.addTopLevelItem(self.physical_node)
        
        self.register_node = QTreeWidgetItem(["Hardware Registers", "", "", ""])
        self.register_node.setFont(0, QFont("Arial", 10, QFont.Weight.Bold))
        self.tag_tree.addTopLevelItem(self.register_node)
        
        self.software_node = QTreeWidgetItem(["Software Variables", "", "", ""])
        self.software_node.setFont(0, QFont("Arial", 10, QFont.Weight.Bold))
        self.tag_tree.addTopLevelItem(self.software_node)
        
        # Expand all nodes
        self.tag_tree.expandAll()
        
        tree_layout.addWidget(self.tag_tree)
        layout.addWidget(tree_group)

    def create_quick_add_section(self, layout):
        """Create quick add section for common tag types"""
        quick_group = QGroupBox("Quick Add")
        quick_layout = QVBoxLayout(quick_group)
        
        # Physical I/O quick add
        self.create_physical_io_quick_add(quick_layout)
        
        layout.addWidget(quick_group)

    def create_physical_io_quick_add(self, layout):
        """Create quick add buttons for physical I/O"""
        io_frame = QFrame()
        io_layout = QVBoxLayout(io_frame)
        
        # Digital I/O section
        digital_layout = QHBoxLayout()
        
        add_di_btn = QPushButton("+ Digital Input")
        add_di_btn.clicked.connect(lambda: self.quick_add_physical_io("Digital Input"))
        digital_layout.addWidget(add_di_btn)
        
        add_do_btn = QPushButton("+ Digital Output")
        add_do_btn.clicked.connect(lambda: self.quick_add_physical_io("Digital Output"))
        digital_layout.addWidget(add_do_btn)
        
        io_layout.addLayout(digital_layout)
        
        # Analog I/O section
        analog_layout = QHBoxLayout()
        
        add_ai_btn = QPushButton("+ Analog Input")
        add_ai_btn.clicked.connect(lambda: self.quick_add_physical_io("Analog Input"))
        analog_layout.addWidget(add_ai_btn)
        
        add_ao_btn = QPushButton("+ Analog Output")
        add_ao_btn.clicked.connect(lambda: self.quick_add_physical_io("Analog Output"))
        analog_layout.addWidget(add_ao_btn)
        
        io_layout.addLayout(analog_layout)
        
        # PWM section
        add_pwm_btn = QPushButton("+ PWM Output")
        add_pwm_btn.clicked.connect(lambda: self.quick_add_physical_io("PWM Output"))
        io_layout.addWidget(add_pwm_btn)
        
        layout.addWidget(io_frame)

    def create_tag_editor_tabs(self, layout):
        """Create tabbed interface for detailed tag editing"""
        self.tab_widget = QTabWidget()
        
        # Physical I/O tab
        self.create_physical_io_tab()
        
        # Hardware registers tab
        self.create_hardware_registers_tab()
        
        # Software variables tab
        self.create_software_variables_tab()
        
        # Memory overview tab
        self.create_memory_overview_tab()
        
        layout.addWidget(self.tab_widget)

    def create_physical_io_tab(self):
        """Create physical I/O configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Physical I/O table
        self.physical_table = QTableWidget(0, 8)
        self.physical_table.setHorizontalHeaderLabels([
            "Tag Name", "I/O Type", "GPIO Pin", "Physical Address", 
            "Data Type", "Initial Value", "Description", "Enabled"
        ])
        
        # Auto-resize columns
        header = self.physical_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Description column
        
        layout.addWidget(self.physical_table)
        
        # Populate with ESP32 I/O pins
        self.populate_physical_io_table()
        
        self.tab_widget.addTab(tab, "Physical I/O")

    def create_hardware_registers_tab(self):
        """Create hardware registers tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Hardware registers table
        self.register_table = QTableWidget(0, 7)
        self.register_table.setHorizontalHeaderLabels([
            "Tag Name", "Register Name", "Physical Address", "Data Type", 
            "Access", "Description", "Enabled"
        ])
        
        header = self.register_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Description column
        
        layout.addWidget(self.register_table)
        
        # Populate with ESP32 registers
        self.populate_hardware_registers_table()
        
        self.tab_widget.addTab(tab, "Hardware Registers")

    def create_software_variables_tab(self):
        """Create software variables tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Software variables table
        self.software_table = QTableWidget(0, 9)
        self.software_table.setHorizontalHeaderLabels([
            "Tag Name", "Data Type", "Initial Value", "Memory Address", 
            "Persistent", "Array Size", "Min Value", "Max Value", "Description"
        ])
        
        header = self.software_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)  # Description column
        
        layout.addWidget(self.software_table)
        
        # Controls for software variables
        controls_layout = QHBoxLayout()
        
        add_var_btn = QPushButton("Add Variable")
        add_var_btn.clicked.connect(self.add_software_variable)
        controls_layout.addWidget(add_var_btn)
        
        remove_var_btn = QPushButton("Remove Variable")
        remove_var_btn.clicked.connect(self.remove_software_variable)
        controls_layout.addWidget(remove_var_btn)
        
        controls_layout.addStretch()
        
        import_btn = QPushButton("Import Tags")
        import_btn.clicked.connect(self.import_tags)
        controls_layout.addWidget(import_btn)
        
        export_btn = QPushButton("Export Tags")
        export_btn.clicked.connect(self.export_tags)
        controls_layout.addWidget(export_btn)
        
        layout.addLayout(controls_layout)
        
        self.tab_widget.addTab(tab, "Software Variables")

    def create_memory_overview_tab(self):
        """Create memory overview and allocation tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Memory usage overview
        memory_group = QGroupBox("ESP32 Memory Usage")
        memory_layout = QFormLayout(memory_group)
        
        self.ram_usage_label = QLabel("0 KB / 1024 KB")
        memory_layout.addRow("RAM Usage:", self.ram_usage_label)
        
        self.flash_usage_label = QLabel("0 KB / 4096 KB")
        memory_layout.addRow("Flash Usage:", self.flash_usage_label)
        
        self.gpio_usage_label = QLabel("0 / 40 pins")
        memory_layout.addRow("GPIO Usage:", self.gpio_usage_label)
        
        layout.addWidget(memory_group)
        
        # Memory map display
        map_group = QGroupBox("Memory Map")
        map_layout = QVBoxLayout(map_group)
        
        self.memory_map_text = QTextEdit()
        self.memory_map_text.setReadOnly(True)
        self.memory_map_text.setMaximumHeight(200)
        map_layout.addWidget(self.memory_map_text)
        
        layout.addWidget(map_group)
        
        # Update memory display
        self.update_memory_overview()
        
        self.tab_widget.addTab(tab, "Memory Overview")

    def create_control_buttons(self, layout):
        """Create control buttons at the bottom"""
        button_layout = QHBoxLayout()
        
        validate_btn = QPushButton("Validate Tags")
        validate_btn.clicked.connect(self.validate_tags)
        button_layout.addWidget(validate_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_tags)
        button_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Load Configuration")
        load_btn.clicked.connect(self.load_tags)
        button_layout.addWidget(load_btn)
        
        layout.addLayout(button_layout)

    def load_esp32_config(self):
        """Load ESP32 configuration from JSON file"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  "templates", "esp32_config.json")
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load ESP32 config: {e}")
            return {}

    def populate_physical_io_table(self):
        """Populate physical I/O table with ESP32 pins"""
        pin_definitions = self.esp32_config.get("pin_definitions", {}).get("digital_io", {})
        
        for i, (pin_name, pin_config) in enumerate(pin_definitions.items()):
            self.physical_table.insertRow(i)
            
            # Tag name
            tag_name = QLineEdit(f"IO_{pin_name}")
            self.physical_table.setCellWidget(i, 0, tag_name)
            
            # I/O Type
            io_type = QComboBox()
            if pin_config.get("type") == "I":
                io_type.addItems(["Digital Input"])
            elif pin_config.get("type") == "IO":
                io_type.addItems(["Digital Input", "Digital Output"])
                if pin_config.get("adc"):
                    io_type.addItem("Analog Input")
            io_type.setCurrentText("Digital Input")
            self.physical_table.setCellWidget(i, 1, io_type)
            
            # GPIO Pin
            self.physical_table.setItem(i, 2, QTableWidgetItem(pin_name))
            
            # Physical Address
            address = f"GPIO_{pin_name.replace('GPIO', '')}"
            self.physical_table.setItem(i, 3, QTableWidgetItem(address))
            
            # Data Type
            data_type = QComboBox()
            data_type.addItems(["BOOL", "BYTE", "INT", "WORD"])
            self.physical_table.setCellWidget(i, 4, data_type)
            
            # Initial Value
            initial_value = QLineEdit("0")
            self.physical_table.setCellWidget(i, 5, initial_value)
            
            # Description
            description = pin_config.get("special", "General purpose I/O")
            self.physical_table.setItem(i, 6, QTableWidgetItem(description))
            
            # Enabled
            enabled = QCheckBox()
            self.physical_table.setCellWidget(i, 7, enabled)

    def populate_hardware_registers_table(self):
        """Populate hardware registers table with ESP32 registers"""
        registers = self.esp32_config.get("esp32_registers", {})
        row = 0
        
        for category, regs in registers.items():
            if category == "metadata":
                continue
                
            for reg_name, reg_info in regs.items():
                self.register_table.insertRow(row)
                
                # Tag name
                tag_name = QLineEdit(f"REG_{reg_name}")
                self.register_table.setCellWidget(row, 0, tag_name)
                
                # Register name
                self.register_table.setItem(row, 1, QTableWidgetItem(reg_name))
                
                # Physical address
                address = reg_info.get("address", "")
                self.register_table.setItem(row, 2, QTableWidgetItem(address))
                
                # Data type
                data_type = reg_info.get("type", "DWORD")
                self.register_table.setItem(row, 3, QTableWidgetItem(data_type))
                
                # Access
                access = reg_info.get("access", "R")
                self.register_table.setItem(row, 4, QTableWidgetItem(access))
                
                # Description
                description = reg_info.get("description", "")
                self.register_table.setItem(row, 5, QTableWidgetItem(description))
                
                # Enabled
                enabled = QCheckBox()
                self.register_table.setCellWidget(row, 6, enabled)
                
                row += 1

    def quick_add_physical_io(self, io_type):
        """Quick add physical I/O tag"""
        # Find next available GPIO pin for this type
        pin_definitions = self.esp32_config.get("pin_definitions", {}).get("digital_io", {})
        
        # Count existing tags of this type
        count = 0
        for i in range(self.physical_table.rowCount()):
            type_widget = self.physical_table.cellWidget(i, 1)
            if isinstance(type_widget, QComboBox) and type_widget.currentText() == io_type:
                enabled_widget = self.physical_table.cellWidget(i, 7)
                if isinstance(enabled_widget, QCheckBox) and enabled_widget.isChecked():
                    count += 1
        
        # Find appropriate pin and enable it
        for i in range(self.physical_table.rowCount()):
            type_widget = self.physical_table.cellWidget(i, 1)
            enabled_widget = self.physical_table.cellWidget(i, 7)
            
            if (isinstance(type_widget, QComboBox) and 
                isinstance(enabled_widget, QCheckBox) and
                not enabled_widget.isChecked()):
                
                # Check if this pin supports the requested type
                pin_item = self.physical_table.item(i, 2)
                if pin_item:
                    pin_name = pin_item.text()
                    pin_config = pin_definitions.get(pin_name, {})
                    
                    # Set appropriate type and enable
                    available_types = [type_widget.itemText(j) for j in range(type_widget.count())]
                    if io_type in available_types:
                        type_widget.setCurrentText(io_type)
                        enabled_widget.setChecked(True)
                        
                        # Update tag name
                        name_widget = self.physical_table.cellWidget(i, 0)
                        if isinstance(name_widget, QLineEdit):
                            prefix = {"Digital Input": "DI", "Digital Output": "DO", 
                                    "Analog Input": "AI", "Analog Output": "AO", "PWM Output": "PWM"}
                            name_widget.setText(f"{prefix.get(io_type, 'IO')}_{count:02d}")
                        
                        self.update_tag_tree()
                        self.tags_modified.emit()
                        break

    def add_software_variable(self):
        """Add a new software variable"""
        row = self.software_table.rowCount()
        self.software_table.insertRow(row)
        
        # Tag name
        tag_name = QLineEdit(f"VAR_{row:03d}")
        self.software_table.setCellWidget(row, 0, tag_name)
        
        # Data type
        data_type = QComboBox()
        data_type.addItems(["BOOL", "BYTE", "INT", "WORD", "DWORD", "FLOAT", "STRING"])
        self.software_table.setCellWidget(row, 1, data_type)
        
        # Initial value
        initial_value = QLineEdit("0")
        self.software_table.setCellWidget(row, 2, initial_value)
        
        # Memory address (auto-allocated)
        try:
            address = self.memory_allocator.allocate_variable("INT")
            address_str = f"0x{address:08X}"
        except Exception as e:
            print(f"Memory allocation error: {e}")
            address_str = "0x3FFAE000"
        
        self.software_table.setItem(row, 3, QTableWidgetItem(address_str))
        
        # Persistent
        persistent = QCheckBox()
        self.software_table.setCellWidget(row, 4, persistent)
        
        # Array size
        array_size = QSpinBox()
        array_size.setMinimum(1)
        array_size.setMaximum(1024)
        self.software_table.setCellWidget(row, 5, array_size)
        
        # Min/Max values
        min_value = QLineEdit("-32768")
        max_value = QLineEdit("32767")
        self.software_table.setCellWidget(row, 6, min_value)
        self.software_table.setCellWidget(row, 7, max_value)
        
        # Description
        description = QLineEdit("User variable")
        self.software_table.setCellWidget(row, 8, description)
        
        self.update_tag_tree()
        self.update_memory_overview()
        self.tags_modified.emit()

    def remove_software_variable(self):
        """Remove selected software variable"""
        current_row = self.software_table.currentRow()
        if current_row >= 0:
            # Free allocated memory
            address_item = self.software_table.item(current_row, 3)
            if address_item:
                try:
                    address_str = address_item.text()
                    # Handle both hex string and integer formats
                    if isinstance(address_str, str):
                        if address_str.startswith('0x'):
                            address = int(address_str, 16)
                        else:
                            address = int(address_str)
                    else:
                        address = int(address_str)
                    self.memory_allocator.free_variable(address)
                except (ValueError, TypeError) as e:
                    print(f"Error freeing memory: {e}")
            
            self.software_table.removeRow(current_row)
            self.update_tag_tree()
            self.update_memory_overview()
            self.tags_modified.emit()

    def on_tag_selected(self):
        """Handle tag selection in tree"""
        current_item = self.tag_tree.currentItem()
        if current_item:
            parent = current_item.parent()
            if parent:
                # Switch to appropriate tab based on selection
                parent_text = parent.text(0)
                if parent_text == "Physical I/O":
                    self.tab_widget.setCurrentIndex(0)
                elif parent_text == "Hardware Registers":
                    self.tab_widget.setCurrentIndex(1)
                elif parent_text == "Software Variables":
                    self.tab_widget.setCurrentIndex(2)

    def update_tag_tree(self):
        """Update the tag tree with current tags"""
        # Clear existing child items
        self.physical_node.takeChildren()
        self.register_node.takeChildren()
        self.software_node.takeChildren()
        
        # Add physical I/O tags
        for i in range(self.physical_table.rowCount()):
            enabled_widget = self.physical_table.cellWidget(i, 7)
            if isinstance(enabled_widget, QCheckBox) and enabled_widget.isChecked():
                name_widget = self.physical_table.cellWidget(i, 0)
                type_widget = self.physical_table.cellWidget(i, 1)
                address_item = self.physical_table.item(i, 3)
                
                if isinstance(name_widget, QLineEdit) and isinstance(type_widget, QComboBox):
                    item = QTreeWidgetItem([
                        name_widget.text(),
                        type_widget.currentText(),
                        address_item.text() if address_item else "",
                        "N/A"
                    ])
                    self.physical_node.addChild(item)
        
        # Add hardware register tags
        for i in range(self.register_table.rowCount()):
            enabled_widget = self.register_table.cellWidget(i, 6)
            if isinstance(enabled_widget, QCheckBox) and enabled_widget.isChecked():
                name_widget = self.register_table.cellWidget(i, 0)
                type_item = self.register_table.item(i, 3)
                address_item = self.register_table.item(i, 2)
                
                if isinstance(name_widget, QLineEdit):
                    item = QTreeWidgetItem([
                        name_widget.text(),
                        type_item.text() if type_item else "",
                        address_item.text() if address_item else "",
                        "N/A"
                    ])
                    self.register_node.addChild(item)
        
        # Add software variable tags
        for i in range(self.software_table.rowCount()):
            name_widget = self.software_table.cellWidget(i, 0)
            type_widget = self.software_table.cellWidget(i, 1)
            address_item = self.software_table.item(i, 3)
            
            if isinstance(name_widget, QLineEdit) and isinstance(type_widget, QComboBox):
                item = QTreeWidgetItem([
                    name_widget.text(),
                    type_widget.currentText(),
                    address_item.text() if address_item else "",
                    "N/A"
                ])
                self.software_node.addChild(item)
        
        # Expand all nodes
        self.tag_tree.expandAll()

    def update_memory_overview(self):
        """Update memory usage display"""
        # Calculate memory usage
        ram_used = self.memory_allocator.get_ram_usage()
        flash_used = 0  # Calculate based on persistent variables
        gpio_used = 0
        
        # Count enabled GPIO pins
        for i in range(self.physical_table.rowCount()):
            enabled_widget = self.physical_table.cellWidget(i, 7)
            if isinstance(enabled_widget, QCheckBox) and enabled_widget.isChecked():
                gpio_used += 1
        
        # Update labels
        self.ram_usage_label.setText(f"{ram_used / 1024:.1f} KB / 1024 KB")
        self.flash_usage_label.setText(f"{flash_used / 1024:.1f} KB / 4096 KB")
        self.gpio_usage_label.setText(f"{gpio_used} / 40 pins")
        
        # Update memory map
        memory_map = self.memory_allocator.get_memory_map()
        self.memory_map_text.setPlainText(memory_map)

    def validate_tags(self):
        """Validate all tag configurations"""
        errors = []
        warnings = []
        
        # Check for duplicate names
        names = set()
        
        # Check physical I/O
        for i in range(self.physical_table.rowCount()):
            enabled_widget = self.physical_table.cellWidget(i, 7)
            if isinstance(enabled_widget, QCheckBox) and enabled_widget.isChecked():
                name_widget = self.physical_table.cellWidget(i, 0)
                if isinstance(name_widget, QLineEdit):
                    name = name_widget.text()
                    if name in names:
                        errors.append(f"Duplicate tag name: {name}")
                    names.add(name)
        
        # Check software variables
        for i in range(self.software_table.rowCount()):
            name_widget = self.software_table.cellWidget(i, 0)
            if isinstance(name_widget, QLineEdit):
                name = name_widget.text()
                if name in names:
                    errors.append(f"Duplicate tag name: {name}")
                names.add(name)
        
        # Show validation results
        if errors:
            QMessageBox.critical(self, "Validation Errors", "\n".join(errors))
        elif warnings:
            QMessageBox.warning(self, "Validation Warnings", "\n".join(warnings))
        else:
            QMessageBox.information(self, "Validation", "All tags are valid!")

    def save_tags(self):
        """Save tag configuration to file"""
        config = self.get_tag_configuration()
        
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      "templates", "tags_config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            QMessageBox.information(self, "Success", "Tag configuration saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save tag configuration:\n{str(e)}")

    def load_tags(self):
        """Load tag configuration from file"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      "templates", "tags_config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self.load_tag_configuration(config)
            QMessageBox.information(self, "Success", "Tag configuration loaded successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tag configuration:\n{str(e)}")

    def load_existing_tags(self):
        """Load existing tags on startup"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      "templates", "tags_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.load_tag_configuration(config)
                print("Existing tag configuration loaded successfully")
            else:
                print("No existing tag configuration found - using defaults")
        except Exception as e:
            print(f"Could not load existing tags: {e}")
            # Continue with empty configuration - don't show error dialog on startup

    def import_tags(self):
        """Import tags from external file"""
        # Implementation for importing tags
        QMessageBox.information(self, "Import", "Tag import functionality to be implemented")

    def export_tags(self):
        """Export tags to external file"""
        # Implementation for exporting tags
        QMessageBox.information(self, "Export", "Tag export functionality to be implemented")

    def get_tag_configuration(self):
        """Get current tag configuration as dictionary"""
        config = {
            "version": "1.0",
            "physical_io": [],
            "hardware_registers": [],
            "software_variables": [],
            "memory_allocation": self.memory_allocator.get_allocation_map()
        }
        
        # Extract physical I/O tags
        for i in range(self.physical_table.rowCount()):
            enabled_widget = self.physical_table.cellWidget(i, 7)
            if isinstance(enabled_widget, QCheckBox) and enabled_widget.isChecked():
                tag_data = self.extract_physical_io_tag(i)
                if tag_data:
                    config["physical_io"].append(tag_data)
        
        # Extract software variables
        for i in range(self.software_table.rowCount()):
            tag_data = self.extract_software_variable_tag(i)
            if tag_data:
                config["software_variables"].append(tag_data)
        
        return config

    def extract_physical_io_tag(self, row):
        """Extract physical I/O tag data from table row"""
        name_widget = self.physical_table.cellWidget(row, 0)
        type_widget = self.physical_table.cellWidget(row, 1)
        pin_item = self.physical_table.item(row, 2)
        address_item = self.physical_table.item(row, 3)
        data_type_widget = self.physical_table.cellWidget(row, 4)
        initial_widget = self.physical_table.cellWidget(row, 5)
        description_item = self.physical_table.item(row, 6)
        
        if (isinstance(name_widget, QLineEdit) and isinstance(type_widget, QComboBox) and
            isinstance(data_type_widget, QComboBox) and isinstance(initial_widget, QLineEdit)):
            
            return {
                "name": name_widget.text(),
                "io_type": type_widget.currentText(),
                "gpio_pin": pin_item.text() if pin_item else "",
                "physical_address": address_item.text() if address_item else "",
                "data_type": data_type_widget.currentText(),
                "initial_value": initial_widget.text(),
                "description": description_item.text() if description_item else ""
            }
        
        return None

    def extract_software_variable_tag(self, row):
        """Extract software variable tag data from table row"""
        name_widget = self.software_table.cellWidget(row, 0)
        type_widget = self.software_table.cellWidget(row, 1)
        initial_widget = self.software_table.cellWidget(row, 2)
        address_item = self.software_table.item(row, 3)
        persistent_widget = self.software_table.cellWidget(row, 4)
        array_widget = self.software_table.cellWidget(row, 5)
        min_widget = self.software_table.cellWidget(row, 6)
        max_widget = self.software_table.cellWidget(row, 7)
        description_widget = self.software_table.cellWidget(row, 8)
        
        if (isinstance(name_widget, QLineEdit) and isinstance(type_widget, QComboBox) and
            isinstance(initial_widget, QLineEdit) and isinstance(persistent_widget, QCheckBox) and
            isinstance(array_widget, QSpinBox) and isinstance(min_widget, QLineEdit) and
            isinstance(max_widget, QLineEdit) and isinstance(description_widget, QLineEdit)):
            
            return {
                "name": name_widget.text(),
                "data_type": type_widget.currentText(),
                "initial_value": initial_widget.text(),
                "memory_address": address_item.text() if address_item else "",
                "persistent": persistent_widget.isChecked(),
                "array_size": array_widget.value(),
                "min_value": min_widget.text(),
                "max_value": max_widget.text(),
                "description": description_widget.text()
            }
        
        return None

    def load_tag_configuration(self, config):
        """Load tag configuration from dictionary"""
        # Clear existing tables
        self.physical_table.setRowCount(0)
        self.software_table.setRowCount(0)
        
        # Restore memory allocator state
        if "memory_allocation" in config:
            self.memory_allocator.restore_allocation_map(config["memory_allocation"])
        
        # Load physical I/O tags
        self.populate_physical_io_table()  # Repopulate with all pins
        
        # Enable and configure physical I/O tags from config
        for tag_config in config.get("physical_io", []):
            self.apply_physical_io_config(tag_config)
        
        # Load software variables
        for tag_config in config.get("software_variables", []):
            self.add_software_variable_from_config(tag_config)
        
        # Update displays
        self.update_tag_tree()
        self.update_memory_overview()

    def apply_physical_io_config(self, tag_config):
        """Apply physical I/O configuration to table"""
        gpio_pin = tag_config.get("gpio_pin", "")
        
        # Find the row with this GPIO pin
        for i in range(self.physical_table.rowCount()):
            pin_item = self.physical_table.item(i, 2)
            if pin_item and pin_item.text() == gpio_pin:
                # Configure this row
                name_widget = self.physical_table.cellWidget(i, 0)
                type_widget = self.physical_table.cellWidget(i, 1)
                data_type_widget = self.physical_table.cellWidget(i, 4)
                initial_widget = self.physical_table.cellWidget(i, 5)
                enabled_widget = self.physical_table.cellWidget(i, 7)
                
                if isinstance(name_widget, QLineEdit):
                    name_widget.setText(tag_config.get("name", ""))
                if isinstance(type_widget, QComboBox):
                    type_widget.setCurrentText(tag_config.get("io_type", ""))
                if isinstance(data_type_widget, QComboBox):
                    data_type_widget.setCurrentText(tag_config.get("data_type", ""))
                if isinstance(initial_widget, QLineEdit):
                    initial_widget.setText(tag_config.get("initial_value", ""))
                if isinstance(enabled_widget, QCheckBox):
                    enabled_widget.setChecked(True)
                
                break

    def add_software_variable_from_config(self, tag_config):
        """Add software variable from configuration"""
        row = self.software_table.rowCount()
        self.software_table.insertRow(row)
        
        # Configure all widgets with loaded data
        name_widget = QLineEdit(tag_config.get("name", ""))
        self.software_table.setCellWidget(row, 0, name_widget)
        
        type_widget = QComboBox()
        type_widget.addItems(["BOOL", "BYTE", "INT", "WORD", "DWORD", "FLOAT", "STRING"])
        type_widget.setCurrentText(tag_config.get("data_type", "INT"))
        self.software_table.setCellWidget(row, 1, type_widget)
        
        initial_widget = QLineEdit(tag_config.get("initial_value", "0"))
        self.software_table.setCellWidget(row, 2, initial_widget)
        
        address = tag_config.get("memory_address", "")
        self.software_table.setItem(row, 3, QTableWidgetItem(address))
        
        persistent_widget = QCheckBox()
        persistent_widget.setChecked(tag_config.get("persistent", False))
        self.software_table.setCellWidget(row, 4, persistent_widget)
        
        array_widget = QSpinBox()
        array_widget.setMinimum(1)
        array_widget.setMaximum(1024)
        array_widget.setValue(tag_config.get("array_size", 1))
        self.software_table.setCellWidget(row, 5, array_widget)
        
        min_widget = QLineEdit(tag_config.get("min_value", "-32768"))
        max_widget = QLineEdit(tag_config.get("max_value", "32767"))
        self.software_table.setCellWidget(row, 6, min_widget)
        self.software_table.setCellWidget(row, 7, max_widget)
        
        description_widget = QLineEdit(tag_config.get("description", ""))
        self.software_table.setCellWidget(row, 8, description_widget)

    def get_tags(self):
        """Legacy method for compatibility"""
        return self.tags

class ESP32MemoryAllocator:
    """Handles ESP32 memory allocation for software variables"""
    
    def __init__(self):
        # ESP32 memory regions
        self.ram_start = 0x3FFAE000  # Start of available RAM
        self.ram_size = 1024 * 1024   # 1024KB available RAM (512KB + 512KB PSRAM allocated)
        self.current_ram_offset = 0
        self.allocated_variables = {}
    
    def allocate_variable(self, data_type, array_size=1):
        """Allocate memory for a variable"""
        type_sizes = {
            "BOOL": 1, "BYTE": 1, "INT": 2, "WORD": 2, 
            "DWORD": 4, "FLOAT": 4, "STRING": 256
        }
        
        size = type_sizes.get(data_type, 4) * array_size
        
        if self.current_ram_offset + size > self.ram_size:
            raise MemoryError("Insufficient RAM for variable allocation")
        
        address = self.ram_start + self.current_ram_offset
        self.allocated_variables[address] = {
            "size": size,
            "type": data_type,
            "array_size": array_size
        }
        
        self.current_ram_offset += size
        return address
    
    def free_variable(self, address):
        """Free allocated variable memory"""
        if address in self.allocated_variables:
            del self.allocated_variables[address]
            # Note: In a real implementation, you'd want to compact memory
    
    def get_ram_usage(self):
        """Get current RAM usage in bytes"""
        return self.current_ram_offset
    
    def get_memory_map(self):
        """Get a text representation of the memory map"""
        lines = ["ESP32 Memory Map:", "=" * 50]
        
        for address, info in sorted(self.allocated_variables.items()):
            lines.append(f"0x{address:08X}: {info['type']} [{info['array_size']}] ({info['size']} bytes)")
        
        lines.append("")
        lines.append(f"Total RAM used: {self.current_ram_offset} bytes")
        lines.append(f"RAM available: {self.ram_size - self.current_ram_offset} bytes")
        
        return "\n".join(lines)
    
    def get_allocation_map(self):
        """Get allocation map for saving"""
        return {
            "current_offset": self.current_ram_offset,
            "allocated_variables": self.allocated_variables
        }
    
    def restore_allocation_map(self, allocation_map):
        """Restore allocation map from saved data"""
        self.current_ram_offset = allocation_map.get("current_offset", 0)
        allocated_vars = allocation_map.get("allocated_variables", {})
        
        # Convert string keys to integers if needed
        self.allocated_variables = {}
        for key, value in allocated_vars.items():
            try:
                # Ensure key is an integer
                if isinstance(key, str):
                    int_key = int(key)
                else:
                    int_key = int(key)
                self.allocated_variables[int_key] = value
            except (ValueError, TypeError) as e:
                print(f"Error converting allocation key {key}: {e}")
                continue

# For testing purposes - allow running this file directly
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Set global stylesheet for testing
    global_style = """
    QTableWidget {
        selection-background-color: #3daee9;
        selection-color: white;
        alternate-background-color: #f0f0f0;
        gridline-color: #d0d0d0;
        background-color: white;
        color: black;
    }
    
    QTableWidget::item:selected {
        background-color: #3daee9;
        color: white;
    }
    
    QTableWidget::item:hover {
        background-color: #e0f0ff;
        color: black;
    }
    
    QTreeWidget {
        selection-background-color: #3daee9;
        selection-color: white;
        alternate-background-color: #f0f0f0;
        background-color: white;
        color: black;
    }
    
    QTreeWidget::item:selected {
        background-color: #3daee9;
        color: white;
    }
    
    QTreeWidget::item:hover {
        background-color: #e0f0ff;
        color: black;
    }
    """
    app.setStyleSheet(global_style)
    
    # Create and show the variable panel for testing
    panel = VariablePanel()
    panel.setWindowTitle("ESP32 PLC Tags/Variables Manager - Test Mode")
    panel.resize(1200, 800)
    panel.show()
    
    sys.exit(app.exec())
