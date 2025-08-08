"""
Enhanced Tag Management System for ESP32 PLC GUI
Provides tag creation, editing, and integration with logic blocks
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QComboBox, QLineEdit, QCheckBox, QSpinBox,
                           QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
                           QWidget, QGroupBox, QGridLayout, QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont
from .tag_model import TagType, AccessType, MemoryType, Tag
import json
import os

# Mapping between display types (shown in UI) and storage types (used in logic)
DISPLAY_TO_STORAGE_TYPE = {
    "Digital Input": "BOOL",
    "Digital Output": "BOOL", 
    "Analog Input": "INT",
    "Analog Output": "INT",
    "BOOL": "BOOL",
    "Boolean": "BOOL",
    "INT": "INT",
    "Integer": "INT",
    "FLOAT": "FLOAT",
    "Float": "FLOAT",
    "STRING": "STRING",
    "String": "STRING",
    "BYTE": "BYTE",
    "Byte": "BYTE",
    "WORD": "WORD", 
    "Word": "WORD",
    "DWORD": "DWORD",
    "Double Word": "DWORD"
}

def normalize_tag_type(display_type):
    """Convert display type to standardized storage type"""
    return DISPLAY_TO_STORAGE_TYPE.get(display_type, display_type)

class TagManager(QObject):
    """Centralized tag management system"""
    
    # Signal emitted when a tag is added
    tag_added = pyqtSignal(str)  # tag name
    
    def __init__(self):
        super().__init__()
        self.tags = {}
        self.load_tags()
    
    def clear_software_tags(self):
        """Clear all software tags, keeping only hardware I/O tags"""
        # Define hardware I/O tag names (from physical GPIO pins)
        hardware_tag_names = ['DO_01', 'AI_00', 'DI_00', 'AI_01', 'DO_00', 'DI_01', 'AI_02', 'IO_GPIO7']
        
        # Keep only hardware tags
        hardware_tags = {}
        for name, tag in self.tags.items():
            if name in hardware_tag_names:
                hardware_tags[name] = tag
        
        self.tags = hardware_tags
        
        # Create a clean JSON file with only hardware tags
        try:
            simple_tags_path = os.path.join(os.path.dirname(__file__), "..", "templates", "simple_tags.json")
            hardware_tag_data = {}
            
            # Add only hardware tags to the JSON
            for name in hardware_tag_names:
                if name in self.tags:
                    tag = self.tags[name]
                    hardware_tag_data[name] = {
                        'name': tag.name,
                        'tag_type': tag.tag_type,
                        'is_array': tag.is_array
                    }
            
            with open(simple_tags_path, 'w') as f:
                json.dump(hardware_tag_data, f, indent=2)
                
            print(f"DEBUG: Cleared and saved hardware-only tags: {list(hardware_tag_data.keys())}")
        except Exception as e:
            print(f"DEBUG: Error updating tags file: {e}")
        
        print(f"DEBUG: Cleared software tags. Remaining hardware tags: {list(self.tags.keys())}")

    def load_tags(self):
        """Load tags from configuration file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "templates", "tags_config.json")
            with open(config_path, 'r') as f:
                tag_data = json.load(f)
                
                # Handle the existing complex format from tags_config.json
                if 'physical_io' in tag_data:
                    for io_item in tag_data['physical_io']:
                        if 'name' in io_item:
                            tag = Tag(
                                name=io_item['name'],
                                tag_type=io_item.get('data_type', 'BOOL'),
                                is_array=False
                            )
                            self.tags[tag.name] = tag
                
                if 'system_registers' in tag_data:
                    for reg_item in tag_data['system_registers']:
                        if 'name' in reg_item:
                            tag = Tag(
                                name=reg_item['name'],
                                tag_type=reg_item.get('data_type', 'INT'),
                                is_array=False
                            )
                            self.tags[tag.name] = tag
                
                # If no tags loaded, create defaults
                if not self.tags:
                    self._create_default_tags()
                    
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default tags if no config exists
            self._create_default_tags()
    
    def save_tags(self):
        """Save tags to configuration file"""
        try:
            # Create a simple tag format for saving new tags
            simple_tags_path = os.path.join(os.path.dirname(__file__), "..", "templates", "simple_tags.json")
            tag_data = {name: {
                'name': tag.name,
                'tag_type': tag.tag_type,
                'is_array': tag.is_array
            } for name, tag in self.tags.items()}
            
            with open(simple_tags_path, 'w') as f:
                json.dump(tag_data, f, indent=2)
        except Exception as e:
            print(f"Error saving tags: {e}")
    
    def _create_default_tags(self):
        """Create default tags for initial setup"""
        default_tags = [
            Tag("on", TagType.BOOL.value),
            Tag("off", TagType.BOOL.value),
            Tag("timer", TagType.INT.value),
            Tag("counter", TagType.INT.value),
            Tag("lessthan", TagType.BOOL.value),
            Tag("bit", TagType.BOOL.value),
        ]
        self.tags = {tag.name: tag for tag in default_tags}
        self.save_tags()
    
    def add_tag(self, tag):
        """Add a new tag"""
        self.tags[tag.name] = tag
        self.save_tags()
        self.tag_added.emit(tag.name)  # Emit signal when tag is added
        
        # Also trigger a global refresh of all tag widgets
        self._refresh_all_tag_widgets()
        
        return True
    
    def _refresh_all_tag_widgets(self):
        """Refresh all TagSelectionWidget instances"""
        # Simple approach: just print debug - the signal system should handle most cases
        print("DEBUG: Global tag refresh triggered - signals should update all widgets")
    
    def get_tag(self, name):
        """Get tag by name"""
        return self.tags.get(name)
    
    def get_all_tags(self):
        """Get all tags"""
        return list(self.tags.values())
    
    def get_tag_names(self):
        """Get list of all tag names"""
        return list(self.tags.keys())
    
    def delete_tag(self, name):
        """Delete a tag"""
        if name in self.tags:
            del self.tags[name]
            self.save_tags()
            return True
        return False

# Global tag manager instance
tag_manager = TagManager()

class NewTagDialog(QDialog):
    """Dialog for creating new tags"""
    
    tag_created = pyqtSignal(str)  # Emit tag name when created
    
    def __init__(self, parent=None, initial_name=""):
        super().__init__(parent)
        self.setWindowTitle("Create New Tag")
        self.setModal(True)
        self.resize(400, 350)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Tag details group
        details_group = QGroupBox("Tag Details")
        details_layout = QGridLayout(details_group)
        
        # Tag name
        details_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_edit = QLineEdit(initial_name)
        details_layout.addWidget(self.name_edit, 0, 1)
        
        # Tag type
        details_layout.addWidget(QLabel("Type:"), 1, 0)
        self.type_combo = QComboBox()
        # Only show software variable types for new tags
        software_types = ["Boolean", "Byte", "Integer", "Word", "Double Word", "Float", "String"]
        self.type_combo.addItems(software_types)
        self.type_combo.setCurrentText("Boolean")
        details_layout.addWidget(self.type_combo, 1, 1)
        
        # Is array
        self.array_check = QCheckBox("Is Array")
        details_layout.addWidget(self.array_check, 2, 0)
        
        # Array size (only enabled when array is checked)
        self.array_size_label = QLabel("Array Size:")
        self.array_size_spin = QSpinBox()
        self.array_size_spin.setRange(1, 1000)
        self.array_size_spin.setValue(10)
        self.array_size_spin.setEnabled(False)
        
        details_layout.addWidget(self.array_size_label, 2, 1)
        details_layout.addWidget(self.array_size_spin, 2, 2)
        
        # Note: Removed Memory and Access dropdowns - new tags are always software variables in RAM with RW access
        
        layout.addWidget(details_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.array_check.toggled.connect(self.array_size_spin.setEnabled)
        self.array_check.toggled.connect(self.array_size_label.setEnabled)
        
        # Validation
        self.name_edit.textChanged.connect(self.validate_input)
        self.validate_input()
    
    def validate_input(self):
        """Validate input and enable/disable OK button"""
        name = self.name_edit.text().strip()
        is_valid = bool(name) and name not in tag_manager.get_tag_names()
        self.ok_button.setEnabled(is_valid)
        
        if name in tag_manager.get_tag_names():
            self.name_edit.setStyleSheet("border: 2px solid red;")
        else:
            self.name_edit.setStyleSheet("")
    
    def get_tag(self):
        """Get the configured tag"""
        return Tag(
            name=self.name_edit.text().strip(),
            tag_type=self.type_combo.currentText(),
            is_array=self.array_check.isChecked()
        )

class TagSelectionWidget(QWidget):
    """Widget for selecting existing tags or creating new ones with type filtering"""
    
    tag_selected = pyqtSignal(str)
    
    def __init__(self, parent=None, allow_creation=True, compatible_types=None):
        super().__init__(parent)
        self.allow_creation = allow_creation
        self.compatible_types = compatible_types or []  # List of compatible data types
        self.block_type = None  # Store block type for debugging
        
        # Try to get block type from parent for better debugging
        if parent and hasattr(parent, 'block_type'):
            self.block_type = parent.block_type
        elif parent and hasattr(parent, 'operator'):
            self.block_type = parent.operator
            
        self.setup_ui()
        self.refresh_tags()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tag selection combo
        self.tag_combo = QComboBox()
        self.tag_combo.setEditable(True)
        self.tag_combo.currentTextChanged.connect(self.on_tag_changed)
        layout.addWidget(self.tag_combo)
        
        if self.allow_creation:
            # New tag button
            self.new_tag_btn = QPushButton("New Tag")
            self.new_tag_btn.clicked.connect(self.create_new_tag)
            layout.addWidget(self.new_tag_btn)
            
            # Tags button
            self.tags_btn = QPushButton("Tags")
            self.tags_btn.clicked.connect(self.open_tags_dialog)
            layout.addWidget(self.tags_btn)
    
    def on_tag_changed(self, text):
        """Handle tag selection change with validation"""
        if text:
            # Validate data type compatibility
            if self.compatible_types and text in tag_manager.tags:
                tag = tag_manager.tags[text]
                if tag.tag_type not in self.compatible_types:
                    # Show warning for incompatible type
                    QMessageBox.warning(self, "Data Type Mismatch", 
                                      f"Tag '{text}' has type '{tag.tag_type}' which is not compatible.\n"
                                      f"This field requires: {', '.join(self.compatible_types)}")
                    self.tag_combo.setCurrentText("")  # Clear invalid selection
                    return
        
        self.tag_selected.emit(text)
    
    def refresh_tags(self):
        """Refresh the tag list without filtering - show all tags, validate on selection"""
        current_text = self.tag_combo.currentText()
        self.tag_combo.clear()
        
        # Always add empty option first
        self.tag_combo.addItem("")
        
        # Add ALL tags without filtering (user requested dropdown removal)
        all_tag_names = tag_manager.get_tag_names()
        if all_tag_names:
            self.tag_combo.addItems(sorted(all_tag_names))
            print(f"DEBUG: Showing all {len(all_tag_names)} tags in dropdown (no filtering)")
        
        # Restore selection if it still exists
        if current_text:
            index = self.tag_combo.findText(current_text)
            if index >= 0:
                self.tag_combo.setCurrentIndex(index)
            else:
                self.tag_combo.setCurrentText("")  # Default to empty if invalid
    
    def set_compatible_types(self, types):
        """Set the compatible data types for this widget"""
        self.compatible_types = types
        self.refresh_tags()
    
    def currentText(self):
        """Get the current text from the combo box"""
        return self.tag_combo.currentText()
    
    def setCurrentText(self, text):
        """Set the current text in the combo box"""
        self.tag_combo.setCurrentText(text)
    
    def addItems(self, items):
        """Add items to the combo box (for backward compatibility)"""
        self.tag_combo.addItems(items)
    
    def create_new_tag(self):
        """Create a new tag"""
        current_text = self.tag_combo.currentText()
        dialog = NewTagDialog(self, current_text)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_tag = dialog.get_tag()
            tag_manager.add_tag(new_tag)
            self.refresh_tags()
            self.tag_combo.setCurrentText(new_tag.name)
            self.tag_selected.emit(new_tag.name)
    
    def open_tags_dialog(self):
        """Open the main tags dialog with optional Select button for logic block context"""
        # Import here to avoid circular imports
        from .variable_panel import VariablePanel
        
        # Create a dialog wrapper for the VariablePanel
        dialog = QDialog(self)
        dialog.setWindowTitle("ESP32-S3-WROOM PLC Tags/Variables Manager")
        dialog.resize(1200, 800)
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Create the variable panel without its own buttons
        variable_panel = VariablePanel(show_buttons=False)
        
        # Set up tag manager reference for auto-save/auto-load
        variable_panel.tag_manager = tag_manager
        
        # Auto-load existing tags when opening
        variable_panel.auto_load_tags()
        
        layout.addWidget(variable_panel)
        
        # Add Select and Cancel buttons (removed Close button per user request)
        button_layout = QHBoxLayout()
        
        select_button = QPushButton("Select")
        cancel_button = QPushButton("Cancel")
        
        # Connect buttons
        def on_select():
            # Auto-save tags first (Select button now also saves)
            variable_panel.auto_save_tags()
            
            print(f"DEBUG: Starting tag selection process for block type: {self.block_type}")
            print(f"DEBUG: Block requires compatible types: {self.compatible_types}")
            print(f"DEBUG: Tags in TagManager: {list(tag_manager.tags.keys())}")
            
            # Try to get the selected tag from variable panel
            try:
                selected_tag, tag_type = variable_panel.get_selected_tag_with_type()
                print(f"DEBUG: Got selected tag: {selected_tag}, type: {tag_type}")
            except Exception as e:
                print(f"DEBUG: Error getting tag with type: {e}")
                # Fallback to basic method if the new method fails
                selected_tag = variable_panel.get_selected_tag()
                tag_type = "BOOL"  # Default type
                print(f"DEBUG: Fallback - selected tag: {selected_tag}, type: {tag_type}")
            
            if selected_tag:
                # Normalize the tag type for compatibility checking
                normalized_type = normalize_tag_type(tag_type)
                print(f"DEBUG: Original type: '{tag_type}' -> Normalized type: '{normalized_type}'")
                
                # Check type compatibility before proceeding
                if self.compatible_types and normalized_type not in self.compatible_types:
                    # Also check if the original display type is in the compatible types
                    if tag_type not in self.compatible_types:
                        print(f"DEBUG: TYPE MISMATCH! Tag '{selected_tag}' has type '{tag_type}' (normalized: '{normalized_type}') but block '{self.block_type}' requires: {self.compatible_types}")
                        # Show warning to user
                        from PyQt6.QtWidgets import QMessageBox
                        QMessageBox.warning(dialog, "Incompatible Data Type", 
                                          f"Tag '{selected_tag}' has type '{tag_type}' which is not compatible with {self.block_type} block.\n\n"
                                          f"This block requires: {', '.join(self.compatible_types)}")
                        return  # Don't proceed with incompatible selection
                
                # Store with normalized type in TagManager
                final_tag_type = normalized_type or "BOOL"
                
                # Ensure the selected tag is in TagManager with proper type
                if not tag_manager.get_tag(selected_tag):
                    from .tag_model import Tag
                    tag_obj = Tag(
                        name=selected_tag,
                        tag_type=final_tag_type
                    )
                    tag_manager.add_tag(tag_obj)
                    print(f"DEBUG: Added new tag to TagManager: {selected_tag} (type: {final_tag_type})")
                
                # Refresh the tag list to include any new tags
                self.refresh_tags()
                
                # Set the selected tag in the combo box
                self.tag_combo.setCurrentText(selected_tag)
                
                # Emit the signal to notify logic block
                self.tag_selected.emit(selected_tag)
                print(f"DEBUG: Tag selected and emitted: {selected_tag} (type: {tag_type}) for block: {self.block_type}")
            else:
                print(f"DEBUG: No tag selected in variable panel for block: {self.block_type}")
                
            dialog.accept()
        
        def on_cancel():
            # Auto-save on cancel as well to preserve any changes
            variable_panel.auto_save_tags()
            dialog.reject()
        
        select_button.clicked.connect(on_select)
        cancel_button.clicked.connect(on_cancel)
        
        button_layout.addWidget(select_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Show dialog
        dialog.exec()
        self.refresh_tags()
    
    def set_current_tag(self, tag_name):
        """Set the currently selected tag"""
        # Refresh tags first to ensure the tag is in the dropdown
        self.refresh_tags()
        self.tag_combo.setCurrentText(tag_name)
    
    def get_current_tag(self):
        """Get the currently selected tag name"""
        return self.tag_combo.currentText()

class TagsDialog(QDialog):
    """Main tags management dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tags")
        self.setModal(True)
        self.resize(800, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Input/Output tab
        io_tab = self.create_io_tab()
        tab_widget.addTab(io_tab, "Input / Output")
        
        # Register tab (placeholder for now)
        register_tab = QWidget()
        tab_widget.addTab(register_tab, "Register")
        
        layout.addWidget(tab_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.help_button = QPushButton("Help")
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.help_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def create_io_tab(self):
        """Create the Input/Output tab"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Left side - categories
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMaximumWidth(150)
        
        categories = ["Input bit", "Input I16", "Input Float", "Output bit", "Output ul16"]
        for category in categories:
            btn = QPushButton(category)
            if category == "Input bit":
                btn.setStyleSheet("background-color: #4a90e2; color: white;")
            left_layout.addWidget(btn)
        
        layout.addWidget(left_widget)
        
        # Right side - tag table
        self.tag_table = QTableWidget()
        self.setup_tag_table()
        layout.addWidget(self.tag_table)
        
        return widget
    
    def setup_tag_table(self):
        """Setup the tag table"""
        headers = ["Name", "Is Array", "Array Size", "Used", "Remote Writable", "Modbus"]
        self.tag_table.setColumnCount(len(headers))
        self.tag_table.setHorizontalHeaderLabels(headers)
        
        # Set column widths
        header = self.tag_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            for i in range(1, len(headers)):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.refresh_tag_table()
    
    def refresh_tag_table(self):
        """Refresh the tag table with current tags"""
        tags = tag_manager.get_all_tags()
        self.tag_table.setRowCount(len(tags))
        
        for row, tag in enumerate(tags):
            # Name
            self.tag_table.setItem(row, 0, QTableWidgetItem(tag.name))
            
            # Is Array
            array_item = QTableWidgetItem()
            array_item.setCheckState(Qt.CheckState.Checked if tag.is_array else Qt.CheckState.Unchecked)
            self.tag_table.setItem(row, 1, array_item)
            
            # Array Size (placeholder)
            self.tag_table.setItem(row, 2, QTableWidgetItem(""))
            
            # Used
            used_item = QTableWidgetItem()
            used_item.setCheckState(Qt.CheckState.Checked)  # Placeholder
            self.tag_table.setItem(row, 3, used_item)
            
            # Remote Writable
            remote_item = QTableWidgetItem()
            remote_item.setCheckState(Qt.CheckState.Unchecked)  # Placeholder
            self.tag_table.setItem(row, 4, remote_item)
            
            # Modbus
            modbus_item = QTableWidgetItem()
            modbus_item.setCheckState(Qt.CheckState.Unchecked)  # Placeholder
            self.tag_table.setItem(row, 5, modbus_item)
