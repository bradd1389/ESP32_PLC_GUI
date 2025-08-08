import json
import os
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QComboBox, QPushButton, QTabWidget, QWidget, QSpinBox, 
                            QCheckBox, QTableWidget, QTableWidgetItem, QGroupBox,
                            QTextEdit, QMessageBox, QProgressBar, QFormLayout,
                            QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

class ESP32TestThread(QThread):
    """Background thread for testing ESP32 connection"""
    result_ready = pyqtSignal(bool, str)
    
    def __init__(self, port, baud_rate):
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
    
    def run(self):
        try:
            ser = serial.Serial(self.port, self.baud_rate, timeout=2)
            # Send AT command or basic ping
            ser.write(b'AT\r\n')
            response = ser.read(100)
            ser.close()
            
            if response:
                self.result_ready.emit(True, f"Connection successful: {response.decode('utf-8', errors='ignore')}")
            else:
                self.result_ready.emit(False, "No response from ESP32")
                
        except Exception as e:
            self.result_ready.emit(False, f"Connection failed: {str(e)}")

class SetupDialog(QDialog):
    # Signals for communicating with tags system
    io_configuration_changed = pyqtSignal(dict)  # Emitted when I/O config changes
    register_mapping_changed = pyqtSignal(dict)  # Emitted when register mapping changes
    
    def __init__(self, parent=None, variable_panel=None):
        super().__init__(parent)
        self.setWindowTitle("ESP32-S3-WROOM PLC Setup")
        self.resize(800, 600)
        
        # Store reference to variable panel for integration
        self.variable_panel = variable_panel
        
        # Configure proper styling to fix highlighting issues
        self.setup_styles()
        
        # Load ESP32 configuration
        self.esp32_config = self.load_esp32_config()
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_communication_tab()
        self.create_io_config_tab()
        self.create_register_mapping_tab()
        self.create_project_settings_tab()
        
        # Setup tags integration if variable panel is available
        if self.variable_panel:
            self.setup_tags_integration()
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        self.test_connection_btn = QPushButton("Test Connection")
        self.test_connection_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_connection_btn)
        
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.clicked.connect(self.save_configuration)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)
        
        main_layout.addLayout(button_layout)
        
        # Load existing configuration
        self.load_configuration()

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
        """
        self.setStyleSheet(style)

    def load_esp32_config(self):
        """Load ESP32 configuration from JSON file"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                  "templates", "esp32_config.json")
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load ESP32 config: {e}")
            return {"esp32_registers": {}, "pin_definitions": {}, "communication_settings": {}}

    def create_communication_tab(self):
        """Create the ESP32 Communication configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Serial Communication Group
        serial_group = QGroupBox("Serial Communication")
        serial_layout = QFormLayout(serial_group)
        
        # Serial port selection
        self.port_combo = QComboBox()
        self.refresh_ports()
        serial_layout.addRow("Serial Port:", self.port_combo)
        
        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.clicked.connect(self.refresh_ports)
        serial_layout.addRow("", refresh_btn)
        
        # Baud rate
        self.baud_combo = QComboBox()
        baud_rates = self.esp32_config.get("communication_settings", {}).get("serial", {}).get("supported_bauds", [115200])
        for baud in baud_rates:
            self.baud_combo.addItem(str(baud))
        self.baud_combo.setCurrentText("115200")
        serial_layout.addRow("Baud Rate:", self.baud_combo)
        
        # Connection status
        self.connection_status = QLabel("Not connected")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        serial_layout.addRow("Status:", self.connection_status)
        
        layout.addWidget(serial_group)
        
        # WiFi Communication Group
        wifi_group = QGroupBox("WiFi Communication (Optional)")
        wifi_layout = QFormLayout(wifi_group)
        
        self.wifi_ssid = QLineEdit()
        wifi_layout.addRow("WiFi SSID:", self.wifi_ssid)
        
        self.wifi_password = QLineEdit()
        self.wifi_password.setEchoMode(QLineEdit.EchoMode.Password)
        wifi_layout.addRow("WiFi Password:", self.wifi_password)
        
        self.wifi_ip = QLineEdit("192.168.1.100")
        wifi_layout.addRow("ESP32 IP Address:", self.wifi_ip)
        
        self.wifi_port = QSpinBox()
        self.wifi_port.setRange(1, 65535)
        self.wifi_port.setValue(80)
        wifi_layout.addRow("Port:", self.wifi_port)
        
        layout.addWidget(wifi_group)
        
        # Device Information Group
        device_group = QGroupBox("Device Information")
        device_layout = QFormLayout(device_group)
        
        self.device_name = QLineEdit("ESP32-S3-WROOM-PLC")
        device_layout.addRow("Device Name:", self.device_name)
        
        self.firmware_version = QLabel("Unknown")
        device_layout.addRow("Firmware Version:", self.firmware_version)
        
        self.chip_id = QLabel("Unknown")
        device_layout.addRow("Chip ID:", self.chip_id)
        
        layout.addWidget(device_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Communication")

    def create_io_config_tab(self):
        """Create the I/O Configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scroll area for I/O configuration
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Digital Inputs Group
        di_group = QGroupBox("Digital Inputs")
        di_layout = QVBoxLayout(di_group)
        
        self.di_table = QTableWidget(8, 4)  # 8 inputs, 4 columns
        self.di_table.setHorizontalHeaderLabels(["Tag Name", "GPIO Pin", "Pull-up", "Invert"])
        
        # Populate digital inputs
        digital_pins = self.esp32_config.get("pin_definitions", {}).get("digital_io", {})
        input_pins = {k: v for k, v in digital_pins.items() if v.get("type") == "I" or v.get("type") == "IO"}
        
        for i, (pin, config) in enumerate(list(input_pins.items())[:8]):
            tag_name = QLineEdit(f"DI_{i:02d}")
            gpio_combo = QComboBox()
            gpio_combo.addItems(input_pins.keys())
            gpio_combo.setCurrentText(pin)
            pullup_check = QCheckBox()
            invert_check = QCheckBox()
            
            self.di_table.setCellWidget(i, 0, tag_name)
            self.di_table.setCellWidget(i, 1, gpio_combo)
            self.di_table.setCellWidget(i, 2, pullup_check)
            self.di_table.setCellWidget(i, 3, invert_check)
        
        di_layout.addWidget(self.di_table)
        scroll_layout.addWidget(di_group)
        
        # Digital Outputs Group
        do_group = QGroupBox("Digital Outputs")
        do_layout = QVBoxLayout(do_group)
        
        self.do_table = QTableWidget(8, 4)  # 8 outputs, 4 columns
        self.do_table.setHorizontalHeaderLabels(["Tag Name", "GPIO Pin", "Initial State", "Invert"])
        
        output_pins = {k: v for k, v in digital_pins.items() if v.get("type") == "IO"}
        for i, (pin, config) in enumerate(list(output_pins.items())[:8]):
            tag_name = QLineEdit(f"DO_{i:02d}")
            gpio_combo = QComboBox()
            gpio_combo.addItems(output_pins.keys())
            gpio_combo.setCurrentText(pin)
            initial_check = QCheckBox()
            invert_check = QCheckBox()
            
            self.do_table.setCellWidget(i, 0, tag_name)
            self.do_table.setCellWidget(i, 1, gpio_combo)
            self.do_table.setCellWidget(i, 2, initial_check)
            self.do_table.setCellWidget(i, 3, invert_check)
        
        do_layout.addWidget(self.do_table)
        scroll_layout.addWidget(do_group)
        
        # Analog Inputs Group
        ai_group = QGroupBox("Analog Inputs")
        ai_layout = QVBoxLayout(ai_group)
        
        self.ai_table = QTableWidget(4, 5)  # 4 inputs, 5 columns
        self.ai_table.setHorizontalHeaderLabels(["Tag Name", "GPIO Pin", "ADC Channel", "Min Value", "Max Value"])
        
        adc_pins = {k: v for k, v in digital_pins.items() if v.get("adc") is not None}
        for i, (pin, config) in enumerate(list(adc_pins.items())[:4]):
            tag_name = QLineEdit(f"AI_{i:02d}")
            gpio_combo = QComboBox()
            gpio_combo.addItems(adc_pins.keys())
            gpio_combo.setCurrentText(pin)
            adc_label = QLabel(config.get("adc", ""))
            min_val = QSpinBox()
            min_val.setRange(0, 4095)
            max_val = QSpinBox()
            max_val.setRange(0, 4095)
            max_val.setValue(4095)
            
            self.ai_table.setCellWidget(i, 0, tag_name)
            self.ai_table.setCellWidget(i, 1, gpio_combo)
            self.ai_table.setCellWidget(i, 2, adc_label)
            self.ai_table.setCellWidget(i, 3, min_val)
            self.ai_table.setCellWidget(i, 4, max_val)
        
        ai_layout.addWidget(self.ai_table)
        scroll_layout.addWidget(ai_group)
        
        # PWM Outputs Group
        pwm_group = QGroupBox("PWM Outputs")
        pwm_layout = QVBoxLayout(pwm_group)
        
        self.pwm_table = QTableWidget(4, 5)  # 4 PWM channels, 5 columns
        self.pwm_table.setHorizontalHeaderLabels(["Tag Name", "GPIO Pin", "Frequency (Hz)", "Resolution (bits)", "Initial Duty %"])
        
        for i in range(4):
            tag_name = QLineEdit(f"PWM_{i:02d}")
            gpio_combo = QComboBox()
            gpio_combo.addItems(output_pins.keys())
            freq_spin = QSpinBox()
            freq_spin.setRange(1, 40000000)
            freq_spin.setValue(5000)
            res_combo = QComboBox()
            res_combo.addItems(["8", "10", "12", "15"])
            duty_spin = QSpinBox()
            duty_spin.setRange(0, 100)
            
            self.pwm_table.setCellWidget(i, 0, tag_name)
            self.pwm_table.setCellWidget(i, 1, gpio_combo)
            self.pwm_table.setCellWidget(i, 2, freq_spin)
            self.pwm_table.setCellWidget(i, 3, res_combo)
            self.pwm_table.setCellWidget(i, 4, duty_spin)
        
        pwm_layout.addWidget(self.pwm_table)
        scroll_layout.addWidget(pwm_group)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.tab_widget.addTab(tab, "I/O Configuration")

    def create_register_mapping_tab(self):
        """Create the Register Mapping tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Register mapping table
        self.register_table = QTableWidget(0, 6)
        self.register_table.setHorizontalHeaderLabels([
            "Tag Name", "Register Name", "Address", "Type", "Access", "Description"
        ])
        
        # Populate with ESP32 registers
        self.populate_register_table()
        
        layout.addWidget(QLabel("Register to Tag Mapping:"))
        layout.addWidget(self.register_table)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Tag")
        add_btn.clicked.connect(self.add_register_mapping)
        button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Tag")
        remove_btn.clicked.connect(self.remove_register_mapping)
        button_layout.addWidget(remove_btn)
        
        button_layout.addStretch()
        
        export_btn = QPushButton("Export Mapping")
        export_btn.clicked.connect(self.export_register_mapping)
        button_layout.addWidget(export_btn)
        
        import_btn = QPushButton("Import Mapping")
        import_btn.clicked.connect(self.import_register_mapping)
        button_layout.addWidget(import_btn)
        
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(tab, "Register Mapping")

    def create_project_settings_tab(self):
        """Create the Project Settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Project Information Group
        project_group = QGroupBox("Project Information")
        project_layout = QFormLayout(project_group)
        
        self.project_name = QLineEdit()
        project_layout.addRow("Project Name:", self.project_name)
        
        self.project_description = QTextEdit()
        self.project_description.setMaximumHeight(80)
        project_layout.addRow("Description:", self.project_description)
        
        self.project_version = QLineEdit("1.0.0")
        project_layout.addRow("Version:", self.project_version)
        
        layout.addWidget(project_group)
        
        # Runtime Settings Group
        runtime_group = QGroupBox("Runtime Settings")
        runtime_layout = QFormLayout(runtime_group)
        
        self.scan_time = QSpinBox()
        self.scan_time.setRange(1, 10000)
        self.scan_time.setValue(100)
        self.scan_time.setSuffix(" ms")
        runtime_layout.addRow("Scan Cycle Time:", self.scan_time)
        
        self.watchdog_enable = QCheckBox()
        self.watchdog_enable.setChecked(True)
        runtime_layout.addRow("Enable Watchdog:", self.watchdog_enable)
        
        self.auto_start = QCheckBox()
        runtime_layout.addRow("Auto-start on boot:", self.auto_start)
        
        layout.addWidget(runtime_group)
        
        # Safety Settings Group
        safety_group = QGroupBox("Safety Settings")
        safety_layout = QFormLayout(safety_group)
        
        self.emergency_stop = QComboBox()
        gpio_pins = list(self.esp32_config.get("pin_definitions", {}).get("digital_io", {}).keys())
        self.emergency_stop.addItems(["None"] + gpio_pins)
        safety_layout.addRow("Emergency Stop Pin:", self.emergency_stop)
        
        self.safe_state_outputs = QCheckBox()
        self.safe_state_outputs.setChecked(True)
        safety_layout.addRow("Safe State on Error:", self.safe_state_outputs)
        
        layout.addWidget(safety_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Project Settings")

    def refresh_ports(self):
        """Refresh the list of available serial ports"""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}")

    def test_connection(self):
        """Test connection to ESP32"""
        if self.port_combo.currentText():
            port = self.port_combo.currentText().split(" - ")[0]
            baud_rate = int(self.baud_combo.currentText())
            
            self.connection_status.setText("Testing...")
            self.connection_status.setStyleSheet("color: orange; font-weight: bold;")
            self.test_connection_btn.setEnabled(False)
            
            # Create and start test thread
            self.test_thread = ESP32TestThread(port, baud_rate)
            self.test_thread.result_ready.connect(self.on_test_result)
            self.test_thread.start()

    def on_test_result(self, success, message):
        """Handle connection test result"""
        if success:
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.connection_status.setText("Failed")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.warning(self, "Connection Test", message)
        
        self.test_connection_btn.setEnabled(True)

    def populate_register_table(self):
        """Populate the register mapping table with ESP32 registers"""
        registers = self.esp32_config.get("esp32_registers", {})
        row = 0
        
        for category, regs in registers.items():
            if category == "metadata":
                continue
                
            for reg_name, reg_info in regs.items():
                self.register_table.insertRow(row)
                
                # Tag name (editable)
                tag_edit = QLineEdit(f"REG_{reg_name}")
                self.register_table.setCellWidget(row, 0, tag_edit)
                
                # Register name
                self.register_table.setItem(row, 1, QTableWidgetItem(reg_name))
                
                # Address
                self.register_table.setItem(row, 2, QTableWidgetItem(reg_info.get("address", "")))
                
                # Type
                self.register_table.setItem(row, 3, QTableWidgetItem(reg_info.get("type", "")))
                
                # Access
                self.register_table.setItem(row, 4, QTableWidgetItem(reg_info.get("access", "")))
                
                # Description
                self.register_table.setItem(row, 5, QTableWidgetItem(reg_info.get("description", "")))
                
                row += 1

    def add_register_mapping(self):
        """Add a new register mapping row"""
        row = self.register_table.rowCount()
        self.register_table.insertRow(row)
        
        tag_edit = QLineEdit(f"NEW_TAG_{row}")
        self.register_table.setCellWidget(row, 0, tag_edit)

    def remove_register_mapping(self):
        """Remove selected register mapping"""
        current_row = self.register_table.currentRow()
        if current_row >= 0:
            self.register_table.removeRow(current_row)

    def export_register_mapping(self):
        """Export register mapping to file"""
        # Implementation for exporting register mappings
        QMessageBox.information(self, "Export", "Register mapping export functionality to be implemented")

    def import_register_mapping(self):
        """Import register mapping from file"""
        # Implementation for importing register mappings
        QMessageBox.information(self, "Import", "Register mapping import functionality to be implemented")

    def load_configuration(self):
        """Load existing configuration"""
        # Load from project file or defaults
        pass

    def save_configuration(self):
        """Save the current configuration"""
        config = self.get_current_configuration()
        
        # Save to project file
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      "templates", "project_config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{str(e)}")

    def get_current_configuration(self):
        """Get the current configuration from all tabs"""
        config = {
            "communication": {
                "serial_port": self.port_combo.currentText().split(" - ")[0] if self.port_combo.currentText() else "",
                "baud_rate": int(self.baud_combo.currentText()),
                "wifi_ssid": self.wifi_ssid.text(),
                "wifi_ip": self.wifi_ip.text(),
                "wifi_port": self.wifi_port.value(),
                "device_name": self.device_name.text()
            },
            "project": {
                "name": self.project_name.text(),
                "description": self.project_description.toPlainText(),
                "version": self.project_version.text(),
                "scan_time": self.scan_time.value(),
                "watchdog_enable": self.watchdog_enable.isChecked(),
                "auto_start": self.auto_start.isChecked(),
                "emergency_stop": self.emergency_stop.currentText(),
                "safe_state_outputs": self.safe_state_outputs.isChecked()
            },
            "io_configuration": {
                # Add I/O configuration extraction here
            },
            "register_mappings": {
                # Add register mapping extraction here
            }
        }
        
        return config

    def setup_tags_integration(self):
        """Setup integration with Tags/Variables system"""
        # Add integration buttons to I/O Configuration tab
        self.add_tags_integration_controls()
        
        # Connect signals for real-time sync
        if hasattr(self, 'di_table'):
            self.di_table.cellChanged.connect(self.on_io_config_changed)
        if hasattr(self, 'do_table'):
            self.do_table.cellChanged.connect(self.on_io_config_changed)
        if hasattr(self, 'ai_table'):
            self.ai_table.cellChanged.connect(self.on_io_config_changed)
        if hasattr(self, 'register_table'):
            self.register_table.cellChanged.connect(self.on_register_mapping_changed)

    def add_tags_integration_controls(self):
        """Add integration controls to I/O Configuration tab"""
        # Find the I/O Configuration tab (index 1)
        io_tab = self.tab_widget.widget(1)
        if io_tab:
            # Create integration controls section
            integration_group = QGroupBox("Tags Integration")
            integration_layout = QVBoxLayout(integration_group)
            
            # Description
            desc_label = QLabel("Synchronize I/O configuration with Tags/Variables system:")
            desc_label.setWordWrap(True)
            integration_layout.addWidget(desc_label)
            
            # Button layout
            button_layout = QHBoxLayout()
            
            # Import from Tags button
            import_btn = QPushButton("← Import from Tags")
            import_btn.setToolTip("Import I/O configuration from Tags/Variables system")
            import_btn.clicked.connect(self.import_from_tags)
            button_layout.addWidget(import_btn)
            
            # Export to Tags button
            export_btn = QPushButton("Export to Tags →")
            export_btn.setToolTip("Export current I/O configuration to Tags/Variables system")
            export_btn.clicked.connect(self.export_to_tags)
            button_layout.addWidget(export_btn)
            
            # Sync button
            sync_btn = QPushButton("⟷ Synchronize")
            sync_btn.setToolTip("Bidirectional synchronization between Setup and Tags")
            sync_btn.clicked.connect(self.synchronize_with_tags)
            button_layout.addWidget(sync_btn)
            
            integration_layout.addLayout(button_layout)
            
            # Status label
            self.sync_status_label = QLabel("Status: Ready for synchronization")
            self.sync_status_label.setStyleSheet("color: green; font-weight: bold;")
            integration_layout.addWidget(self.sync_status_label)
            
            # Add to the I/O tab layout
            io_layout = io_tab.layout()
            if io_layout:
                io_layout.addWidget(integration_group)

    def import_from_tags(self):
        """Import I/O configuration from Tags/Variables system"""
        if not self.variable_panel:
            QMessageBox.warning(self, "Integration Error", 
                              "Tags/Variables system is not available.")
            return
        
        try:
            # Get tag configuration from variable panel
            tag_config = self.variable_panel.get_tag_configuration()
            
            # Clear existing I/O configuration
            if hasattr(self, 'di_table'):
                self.di_table.setRowCount(0)
            if hasattr(self, 'do_table'):
                self.do_table.setRowCount(0)
            if hasattr(self, 'ai_table'):
                self.ai_table.setRowCount(0)
            
            # Import physical I/O tags
            physical_io = tag_config.get('physical_io', [])
            for tag in physical_io:
                if not tag.get('enabled', False):
                    continue
                    
                io_type = tag.get('io_type', '')
                
                if io_type == 'Digital Input':
                    self.add_digital_input_from_tag(tag)
                elif io_type == 'Digital Output':
                    self.add_digital_output_from_tag(tag)
                elif io_type == 'Analog Input':
                    self.add_analog_input_from_tag(tag)
            
            self.sync_status_label.setText("Status: Successfully imported from Tags")
            self.sync_status_label.setStyleSheet("color: green; font-weight: bold;")
            
            QMessageBox.information(self, "Import Complete", 
                                  f"Imported {len(physical_io)} I/O configurations from Tags system.")
            
        except Exception as e:
            self.sync_status_label.setText(f"Status: Import failed - {str(e)}")
            self.sync_status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.critical(self, "Import Error", f"Failed to import from Tags:\n{str(e)}")

    def export_to_tags(self):
        """Export current I/O configuration to Tags/Variables system"""
        if not self.variable_panel:
            QMessageBox.warning(self, "Integration Error", 
                              "Tags/Variables system is not available.")
            return
        
        try:
            # Extract I/O configuration from Setup dialog
            io_config = self.extract_io_configuration()
            
            # Clear existing physical I/O in tags
            self.variable_panel.physical_table.setRowCount(0)
            self.variable_panel.populate_physical_io_table()
            
            # Add I/O configurations to tags
            exported_count = 0
            
            for config_type, configs in io_config.items():
                for config in configs:
                    if self.add_tag_from_io_config(config_type, config):
                        exported_count += 1
            
            # Update tag tree and displays
            self.variable_panel.update_tag_tree()
            self.variable_panel.update_memory_overview()
            
            self.sync_status_label.setText("Status: Successfully exported to Tags")
            self.sync_status_label.setStyleSheet("color: green; font-weight: bold;")
            
            QMessageBox.information(self, "Export Complete", 
                                  f"Exported {exported_count} I/O configurations to Tags system.")
            
        except Exception as e:
            self.sync_status_label.setText(f"Status: Export failed - {str(e)}")
            self.sync_status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.critical(self, "Export Error", f"Failed to export to Tags:\n{str(e)}")

    def synchronize_with_tags(self):
        """Bidirectional synchronization between Setup and Tags"""
        if not self.variable_panel:
            QMessageBox.warning(self, "Integration Error", 
                              "Tags/Variables system is not available.")
            return
        
        reply = QMessageBox.question(self, "Synchronize", 
                                   "This will synchronize I/O configurations between Setup and Tags.\n" +
                                   "Current configurations in both systems may be overwritten.\n\n" +
                                   "Continue?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # First export Setup → Tags
                self.export_to_tags()
                
                # Then update Setup with any Tags-specific configurations
                self.import_from_tags()
                
                self.sync_status_label.setText("Status: Synchronization complete")
                self.sync_status_label.setStyleSheet("color: blue; font-weight: bold;")
                
            except Exception as e:
                self.sync_status_label.setText(f"Status: Sync failed - {str(e)}")
                self.sync_status_label.setStyleSheet("color: red; font-weight: bold;")
                QMessageBox.critical(self, "Sync Error", f"Synchronization failed:\n{str(e)}")

    def add_digital_input_from_tag(self, tag):
        """Add digital input configuration from tag"""
        if not hasattr(self, 'di_table'):
            return
        
        row = self.di_table.rowCount()
        self.di_table.insertRow(row)
        
        # Pin
        self.di_table.setItem(row, 0, QTableWidgetItem(tag.get('gpio_pin', '').replace('GPIO', '')))
        
        # Mode
        mode_combo = QComboBox()
        mode_combo.addItems(["INPUT", "INPUT_PULLUP", "INPUT_PULLDOWN"])
        mode_combo.setCurrentText(tag.get('pin_mode', 'INPUT'))
        self.di_table.setCellWidget(row, 1, mode_combo)
        
        # Interrupt
        interrupt_combo = QComboBox()
        interrupt_combo.addItems(["NONE", "RISING", "FALLING", "CHANGE"])
        interrupt_combo.setCurrentText(tag.get('interrupt_mode', 'NONE'))
        self.di_table.setCellWidget(row, 2, interrupt_combo)
        
        # Tag Name
        self.di_table.setItem(row, 3, QTableWidgetItem(tag.get('name', '')))

    def add_digital_output_from_tag(self, tag):
        """Add digital output configuration from tag"""
        if not hasattr(self, 'do_table'):
            return
        
        row = self.do_table.rowCount()
        self.do_table.insertRow(row)
        
        # Pin
        self.do_table.setItem(row, 0, QTableWidgetItem(tag.get('gpio_pin', '').replace('GPIO', '')))
        
        # Mode
        mode_combo = QComboBox()
        mode_combo.addItems(["OUTPUT", "OUTPUT_OPEN_DRAIN"])
        mode_combo.setCurrentText(tag.get('pin_mode', 'OUTPUT'))
        self.do_table.setCellWidget(row, 1, mode_combo)
        
        # Initial State
        initial_combo = QComboBox()
        initial_combo.addItems(["LOW", "HIGH"])
        initial_state = "HIGH" if tag.get('initial_value', '0') == '1' else "LOW"
        initial_combo.setCurrentText(initial_state)
        self.do_table.setCellWidget(row, 2, initial_combo)
        
        # Tag Name
        self.do_table.setItem(row, 3, QTableWidgetItem(tag.get('name', '')))

    def add_analog_input_from_tag(self, tag):
        """Add analog input configuration from tag"""
        if not hasattr(self, 'ai_table'):
            return
        
        row = self.ai_table.rowCount()
        self.ai_table.insertRow(row)
        
        # Pin
        self.ai_table.setItem(row, 0, QTableWidgetItem(tag.get('gpio_pin', '').replace('GPIO', '')))
        
        # Resolution
        resolution_combo = QComboBox()
        resolution_combo.addItems(["9", "10", "11", "12"])
        resolution_combo.setCurrentText("12")  # Default
        self.ai_table.setCellWidget(row, 1, resolution_combo)
        
        # Attenuation
        atten_combo = QComboBox()
        atten_combo.addItems(["0dB", "2.5dB", "6dB", "11dB"])
        atten_combo.setCurrentText("11dB")  # Default for 3.3V
        self.ai_table.setCellWidget(row, 2, atten_combo)
        
        # Samples
        samples_spin = QSpinBox()
        samples_spin.setRange(1, 255)
        samples_spin.setValue(64)  # Default
        self.ai_table.setCellWidget(row, 3, samples_spin)
        
        # Tag Name
        self.ai_table.setItem(row, 4, QTableWidgetItem(tag.get('name', '')))

    def extract_io_configuration(self):
        """Extract I/O configuration from Setup dialog tables"""
        config = {
            'digital_inputs': [],
            'digital_outputs': [],
            'analog_inputs': []
        }
        
        # Extract digital inputs
        if hasattr(self, 'di_table'):
            for row in range(self.di_table.rowCount()):
                pin_item = self.di_table.item(row, 0)
                mode_widget = self.di_table.cellWidget(row, 1)
                interrupt_widget = self.di_table.cellWidget(row, 2)
                name_item = self.di_table.item(row, 3)
                
                if pin_item and pin_item.text():
                    config['digital_inputs'].append({
                        'gpio_pin': f"GPIO{pin_item.text()}",
                        'pin_mode': mode_widget.currentText() if isinstance(mode_widget, QComboBox) else 'INPUT',
                        'interrupt_mode': interrupt_widget.currentText() if isinstance(interrupt_widget, QComboBox) else 'NONE',
                        'debounce_time': 50,  # Default
                        'name': name_item.text() if name_item else f"DI_{pin_item.text()}",
                        'description': ''
                    })
        
        # Extract digital outputs
        if hasattr(self, 'do_table'):
            for row in range(self.do_table.rowCount()):
                pin_item = self.do_table.item(row, 0)
                mode_widget = self.do_table.cellWidget(row, 1)
                initial_widget = self.do_table.cellWidget(row, 2)
                name_item = self.do_table.item(row, 3)
                
                if pin_item and pin_item.text():
                    config['digital_outputs'].append({
                        'gpio_pin': f"GPIO{pin_item.text()}",
                        'pin_mode': mode_widget.currentText() if isinstance(mode_widget, QComboBox) else 'OUTPUT',
                        'initial_value': '1' if (isinstance(initial_widget, QComboBox) and initial_widget.currentText() == 'HIGH') else '0',
                        'name': name_item.text() if name_item else f"DO_{pin_item.text()}",
                        'description': ''
                    })
        
        # Extract analog inputs
        if hasattr(self, 'ai_table'):
            for row in range(self.ai_table.rowCount()):
                pin_item = self.ai_table.item(row, 0)
                name_item = self.ai_table.item(row, 4)
                
                if pin_item and pin_item.text():
                    config['analog_inputs'].append({
                        'gpio_pin': f"GPIO{pin_item.text()}",
                        'scale_min': 0,  # Default
                        'scale_max': 100,  # Default
                        'name': name_item.text() if name_item else f"AI_{pin_item.text()}",
                        'description': ''
                    })
        
        return config

    def add_tag_from_io_config(self, config_type, config):
        """Add tag to variable panel from I/O configuration"""
        if not self.variable_panel:
            return False
        
        # Map config types to I/O types
        io_type_map = {
            'digital_inputs': 'Digital Input',
            'digital_outputs': 'Digital Output',
            'analog_inputs': 'Analog Input'
        }
        
        io_type = io_type_map.get(config_type)
        if not io_type:
            return False
        
        # Find available row in physical table
        table = self.variable_panel.physical_table
        
        # Look for existing row with matching GPIO pin
        for row in range(table.rowCount()):
            pin_item = table.item(row, 2)
            if pin_item and pin_item.text() == config.get('gpio_pin', ''):
                # Update existing row
                name_widget = table.cellWidget(row, 0)
                type_widget = table.cellWidget(row, 1)
                enabled_widget = table.cellWidget(row, 7)
                
                if isinstance(name_widget, QLineEdit):
                    name_widget.setText(config.get('name', ''))
                if isinstance(type_widget, QComboBox):
                    # Check if this I/O type is available for this pin
                    available_types = [type_widget.itemText(i) for i in range(type_widget.count())]
                    if io_type in available_types:
                        type_widget.setCurrentText(io_type)
                if isinstance(enabled_widget, QCheckBox):
                    enabled_widget.setChecked(True)
                
                return True
        
        return False

    def on_io_config_changed(self):
        """Handle I/O configuration changes"""
        if self.variable_panel:
            # Extract current configuration and update tags
            io_config = self.extract_io_configuration()
            self.io_configuration_changed.emit(io_config)

    def on_register_mapping_changed(self):
        """Handle register mapping changes"""
        if self.variable_panel:
            # Extract register mappings and update tags
            register_mappings = {}  # Extract from register table
            self.register_mapping_changed.emit(register_mappings)
