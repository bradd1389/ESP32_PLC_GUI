from PyQt6.QtWidgets import QWidget, QVBoxLayout
from editor.draggable_block import DraggableButton
import json
import os

class Toolbox(QWidget):
    def __init__(self, canvas):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Load block configuration
        self.block_config = self.load_block_config()
        
        # Create buttons from configuration
        for block_name in self.block_config.get("block_types", {}):
            layout.addWidget(DraggableButton(block_name))
        
        self.setLayout(layout)
    
    def load_block_config(self):
        """Load block configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "templates", "block_config.json")
            with open(config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback to hardcoded list if config file not found
            block_names = [
                "Wire Router", "ON?", "OFF?", "<", ">", "<=", ">=", "=", "≠",
                "Turn On/Off", "Calculator", "Copy", "Counter", "Filter", "Motion In", "Motion Out",
                "PID", "PWM", "Ramp", "Scale", "Shift / Rotate", "Statistics", "Subroutine", 
                "Timer / Clock", "Note", "Code Block"
            ]
            fallback_config = {"block_types": {}}
            for block_name in block_names:
                width = 75 if block_name == "Wire Router" else 100
                fallback_config["block_types"][block_name] = {"width": width, "height": 40}
            return fallback_config

    def refresh_toolbox(self):
        """Refresh the toolbox by reloading configuration and recreating buttons"""
        # Clear existing layout
        layout = self.layout()
        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child and child.widget():
                    widget = child.widget()
                    if widget:
                        widget.deleteLater()
            
            # Reload configuration and recreate buttons
            self.block_config = self.load_block_config()
            for block_name in self.block_config.get("block_types", {}):
                layout.addWidget(DraggableButton(block_name))
