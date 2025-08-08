
import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QDockWidget, QWidget, QVBoxLayout, QPushButton, QMenu, QDialog, QFileDialog, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QTimer

from editor.flowchart_canvas import FlowchartCanvas
from editor.toolbox import Toolbox
from editor.project_panel import ProjectPanel
from editor.setup_dialog import SetupDialog

# Import tag manager for synchronization
try:
    from editor.tag_integration import tag_manager
except ImportError:
    tag_manager = None

# Import improved error handling and utilities
from utils import (
    get_logger, ErrorHandler, ProjectFileError, ProjectDataError,
    validate_file_path, validate_json_file, validate_project_data,
    log_method_entry
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize logger
        self.logger = get_logger('MainWindow')
        self.logger.info("Initializing ESP32 PLC GUI Main Window")
        
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.resize(1400,800)
        self.setWindowTitle("Embedded PLC Flowchart GUI")
        self.canvas = FlowchartCanvas(self)
        self.setCentralWidget(self.canvas)
        
        # Connect to track project modifications
        self.canvas.project_modified.connect(self.mark_project_modified)

        self.td = QDockWidget("Logic Blocks",self)
        self.td.setWidget(Toolbox(self.canvas))
        self.td.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,self.td)

        self.pd = QDockWidget("Solution",self)
        self.pd.setWidget(ProjectPanel())
        self.pd.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.pd)

        # Setup button (pop-out) placed in menu bar to the right of File menu
        setup_btn = QPushButton("Setup", self)
        setup_btn.setFixedWidth(80)
        setup_btn.clicked.connect(self.show_setup_dialog)
        self.setup_btn = setup_btn

        # Custom menu bar widget for precise placement and compact style
        from PyQt6.QtWidgets import QHBoxLayout
        menu_widget = QWidget(self)
        menu_layout = QHBoxLayout(menu_widget)
        menu_layout.setContentsMargins(2, 2, 2, 2)
        menu_layout.setSpacing(2)

        btn_style = "QPushButton { min-width: 50px; max-width: 60px; min-height: 22px; max-height: 24px; font-size: 10pt; }"

        # File menu
        file_menu = QMenu("File", self)
        act_new = QAction("New Project", self)
        act_open = QAction("Open Project", self)
        act_save = QAction("Save Project", self)
        act_saveas = QAction("Save Project As", self)
        file_menu.addAction(act_new)
        file_menu.addAction(act_open)
        file_menu.addAction(act_save)
        file_menu.addAction(act_saveas)
        file_menu_btn = QPushButton("File", self)
        file_menu_btn.setMenu(file_menu)
        file_menu_btn.setStyleSheet(btn_style)
        menu_layout.addWidget(file_menu_btn)

        # Setup button
        self.setup_btn.setStyleSheet(btn_style)
        menu_layout.addWidget(self.setup_btn)

        # View menu
        view_menu = QMenu("View", self)
        act_toolbox = QAction("Show Toolbox", self)
        act_toolbox.triggered.connect(self.td.show)
        view_menu.addAction(act_toolbox)
        act_project = QAction("Show Project", self)
        act_project.triggered.connect(self.pd.show)
        view_menu.addAction(act_project)
        view_menu.addSeparator()
        act_refresh = QAction("Reload Block Config", self)
        act_refresh.triggered.connect(self.refresh_block_config)
        view_menu.addAction(act_refresh)
        view_menu_btn = QPushButton("View", self)
        view_menu_btn.setMenu(view_menu)
        view_menu_btn.setStyleSheet(btn_style)
        menu_layout.addWidget(view_menu_btn)

        # Debug menu
        debug_menu = QMenu("Debug", self)
        self.debug_mode_action = QAction("Enable Debug Mode", self)
        self.debug_mode_action.setCheckable(True)
        self.debug_mode_action.triggered.connect(self.toggle_debug_mode)
        debug_menu.addAction(self.debug_mode_action)
        
        self.show_values_action = QAction("Show Values", self)
        self.show_values_action.setCheckable(True)
        self.show_values_action.setEnabled(False)  # Disabled until debug mode is enabled
        self.show_values_action.triggered.connect(self.toggle_show_values)
        debug_menu.addAction(self.show_values_action)
        
        debug_menu_btn = QPushButton("Debug", self)
        debug_menu_btn.setMenu(debug_menu)
        debug_menu_btn.setStyleSheet(btn_style)
        menu_layout.addWidget(debug_menu_btn)

        # Tags action as a button
        act_tags = QAction("Tags", self)
        tags_btn = QPushButton("Tags", self)
        tags_btn.setStyleSheet(btn_style)
        menu_layout.addWidget(tags_btn)

        menu_layout.addStretch(1)
        self.setMenuWidget(menu_widget)

        # Tags panel as a resizable dialog
        from editor.variable_panel import VariablePanel
        self.tag_dialog = QDialog(self)
        self.tag_dialog.setWindowTitle("ESP32-S3-WROOM PLC Tags/Variables Manager")
        self.tag_dialog.resize(1200, 800)  # Larger size for enhanced interface
        tag_layout = QVBoxLayout(self.tag_dialog)
        
        # Create the enhanced variable panel
        self.variable_panel = VariablePanel()
        # Set up tag manager reference for auto-save/auto-load functionality
        self.variable_panel.tag_manager = tag_manager
        tag_layout.addWidget(self.variable_panel)
        self.tag_dialog.setSizeGripEnabled(True)
        
        # Connect variable panel signals
        self.variable_panel.tags_modified.connect(self.mark_project_modified)
        
        # Connect to TagManager signals to refresh main window tags when tags are added from logic blocks
        if tag_manager is not None:
            tag_manager.tag_added.connect(self.on_external_tag_added)

        def show_tag_dialog():
            # Refresh the variable panel to show any new tags added from logic blocks
            if hasattr(self.variable_panel, 'update_tag_tree'):
                self.variable_panel.update_tag_tree()
            
            # Center the dialog in the main window
            parent_geom = self.geometry()
            dlg_geom = self.tag_dialog.frameGeometry()
            center_point = parent_geom.center()
            dlg_geom.moveCenter(center_point)
            self.tag_dialog.move(dlg_geom.topLeft())
            self.tag_dialog.show()

        tags_btn.clicked.connect(show_tag_dialog)

        # Connect file menu actions
        act_new.triggered.connect(lambda: self.new_project())
        act_open.triggered.connect(lambda: self.open_project())
        act_save.triggered.connect(lambda: self.save_project())
        act_saveas.triggered.connect(lambda: self.save_project_as())
        
        # Initialize project state
        self.current_project_file = None
        self.project_modified = False
        
        # Show startup dialog after UI is fully initialized
        QTimer.singleShot(100, self.show_startup_dialog)
        
        QTimer.singleShot(0,lambda: self.canvas.ensureVisible(0,0,1,1))

    def show_setup_dialog(self):
        # Pass the variable panel to setup dialog for integration
        variable_panel = getattr(self, 'variable_panel', None)
        dlg = SetupDialog(self, variable_panel)
        dlg.exec()

    def on_external_tag_added(self, tag_name):
        """Called when a tag is added to TagManager from logic blocks"""
        # Refresh the main window's variable panel to show the new tag
        if hasattr(self.variable_panel, 'on_external_tag_added'):
            self.variable_panel.on_external_tag_added(tag_name)

    def refresh_block_config(self):
        """Reload block configuration from JSON file"""
        # Refresh the toolbox
        toolbox_widget = self.td.widget()
        if toolbox_widget:
            # Duck typing: if it has the method, call it
            refresh_method = getattr(toolbox_widget, 'refresh_toolbox', None)
            if refresh_method:
                refresh_method()
                print("Block configuration reloaded successfully!")
            else:
                print("Toolbox refresh method not available")

    def toggle_debug_mode(self):
        """Toggle debug mode for all logic blocks"""
        debug_enabled = self.debug_mode_action.isChecked()
        self.show_values_action.setEnabled(debug_enabled)
        
        # Update all logic blocks in the canvas
        if self.canvas and self.canvas.scene():
            scene = self.canvas.scene()
            if scene:
                from editor.logic_blocks import LogicBlock
                for item in scene.items():
                    if isinstance(item, LogicBlock):
                        item.toggle_debug_mode(debug_enabled)
        
        if debug_enabled:
            print("Debug mode enabled - logic blocks will show configuration details")
        else:
            print("Debug mode disabled")
            # Reset show values to False when debug mode is disabled
            self.show_values_action.setChecked(False)

    def toggle_show_values(self):
        """Toggle between showing tag names and values in debug mode"""
        if self.canvas and self.canvas.scene():
            scene = self.canvas.scene()
            if scene:
                from editor.logic_blocks import LogicBlock
                for item in scene.items():
                    if isinstance(item, LogicBlock):
                        item.toggle_value_display()
        
        if self.show_values_action.isChecked():
            print("Showing tag values in logic blocks")
        else:
            print("Showing tag names in logic blocks")

    @log_method_entry
    def new_project(self):
        """Create a new project with improved error handling"""
        self.logger.info("Creating new project")
        
        # Early return if user cancels unsaved changes confirmation
        if not self._confirm_unsaved_changes("New Project"):
            return False

        # Ask user for project name and location
        project_info = self._get_new_project_info()
        if not project_info:
            return False  # User cancelled
        
        project_name, project_path = project_info

        try:
            # Clear the canvas and reset tags
            self.canvas.clear_canvas()
            
            # Clear software tags for new project (keep only hardware I/O)
            from editor.tag_integration import tag_manager
            if tag_manager:
                tag_manager.clear_software_tags()
            
            # Reset the variable panel
            if hasattr(self, 'variable_panel'):
                self._reset_variable_panel()
                # Refresh to show only hardware tags
                if hasattr(self.variable_panel, 'auto_load_tags'):
                    self.variable_panel.auto_load_tags()
            
            # Set the new project file path
            self.current_project_file = project_path
            self.project_modified = False
            
            # Update window title with project name
            self.setWindowTitle(f"Embedded PLC Flowchart GUI - {project_name}")
            
            # Update solution panel if it exists
            if hasattr(self, 'pd') and self.pd.widget():
                project_panel = self.pd.widget()
                # Use duck typing to check if the method exists
                if hasattr(project_panel, 'update_project_name'):
                    try:
                        project_panel.update_project_name(project_name)  # type: ignore
                    except Exception as e:
                        print(f"DEBUG: Error updating project panel: {e}")
                else:
                    print("DEBUG: ProjectPanel doesn't have update_project_name method")
            else:
                print("DEBUG: Solution panel (pd) not found or has no widget")
            
            self.logger.info("New project created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create new project: {e}")
            ErrorHandler.handle_exception(e, self)
            return False

    def _get_new_project_info(self):
        """Get project name and location from user"""
        from PyQt6.QtWidgets import QInputDialog, QFileDialog
        import os
        
        # Get project name
        project_name, ok = QInputDialog.getText(
            self, 
            'New Project', 
            'Enter project name:',
            text='MyProject'
        )
        
        if not ok or not project_name.strip():
            return None
        
        project_name = project_name.strip()
        
        # Get project location
        project_dir = QFileDialog.getExistingDirectory(
            self,
            'Select Project Location',
            os.path.expanduser('~/Documents')
        )
        
        if not project_dir:
            return None
        
        # Create full project path
        project_path = os.path.join(project_dir, f"{project_name}.plc")
        
        return project_name, project_path

    def show_startup_dialog(self):
        """Show startup dialog to choose between new project or open existing"""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("ESP32 PLC GUI - Project Selection")
        msg.setText("Welcome to ESP32 PLC GUI")
        msg.setInformativeText("Would you like to create a new project or open an existing one?")
        msg.setIcon(QMessageBox.Icon.Question)
        
        # Custom buttons
        new_btn = msg.addButton("New Project", QMessageBox.ButtonRole.AcceptRole)
        open_btn = msg.addButton("Open Existing", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg.addButton("Skip", QMessageBox.ButtonRole.RejectRole)
        
        msg.setDefaultButton(new_btn)
        
        # Center the dialog on the main window
        msg.move(
            self.geometry().center().x() - msg.width() // 2,
            self.geometry().center().y() - msg.height() // 2
        )
        
        # Execute dialog and handle response
        result = msg.exec()
        
        if msg.clickedButton() == new_btn:
            self.new_project()
        elif msg.clickedButton() == open_btn:
            self.open_project()
        elif msg.clickedButton() == cancel_btn:
            # User skipped - leave with current state but clear software tags
            self._reset_to_empty_project()

    def _reset_to_empty_project(self):
        """Reset to an empty project state with no tags"""
        self.canvas.clear_canvas()
        
        # Clear software tags (keep only hardware I/O)
        from editor.tag_integration import tag_manager
        if tag_manager:
            tag_manager.clear_software_tags()
        
        if hasattr(self, 'variable_panel'):
            self._reset_variable_panel()
            # Refresh to show only hardware tags
            if hasattr(self.variable_panel, 'auto_load_tags'):
                self.variable_panel.auto_load_tags()
                
        self.current_project_file = None
        self.project_modified = False
        self.setWindowTitle("Embedded PLC Flowchart GUI - Untitled Project")
        
        # Update solution panel with default name
        if hasattr(self, 'pd') and self.pd.widget():
            project_panel = self.pd.widget()
            if hasattr(project_panel, 'update_project_name'):
                try:
                    project_panel.update_project_name("Untitled Project")  # type: ignore
                except Exception as e:
                    print(f"DEBUG: Error updating project panel: {e}")

    def _confirm_unsaved_changes(self, operation_name: str) -> bool:
        """
        Confirm with user if they want to proceed with unsaved changes
        
        Args:
            operation_name: Name of the operation (e.g., "New Project", "Open Project")
        
        Returns:
            True if user confirms or no unsaved changes, False if user cancels
        """
        if not self.project_modified:
            return True
        
        reply = QMessageBox.question(
            self, 
            operation_name, 
            'Current project has unsaved changes. Continue?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def _reset_variable_panel(self):
        """Reset the variable panel to default state"""
        try:
            # Clear existing tags and reload default configuration
            self.variable_panel.physical_table.setRowCount(0)
            self.variable_panel.software_table.setRowCount(0)
            
            # Import and reset memory allocator
            from editor.variable_panel import ESP32MemoryAllocator
            self.variable_panel.memory_allocator = ESP32MemoryAllocator()
            
            self.variable_panel.populate_physical_io_table()
            self.variable_panel.populate_hardware_registers_table()
            self.variable_panel.update_tag_tree()
            self.variable_panel.update_memory_overview()
            
        except Exception as e:
            self.logger.warning(f"Failed to reset variable panel: {e}")
            # Don't fail the entire operation for variable panel issues

    @log_method_entry
    def open_project(self):
        """Open an existing project with improved error handling and early returns"""
        self.logger.info("Opening project")
        
        # Early return if user cancels unsaved changes confirmation
        if not self._confirm_unsaved_changes("Open Project"):
            return False

        # Early return if no file selected
        file_path = self._get_project_file_path()
        if not file_path:
            return False

        # Load and apply project data
        try:
            project_data = self._load_project_data(file_path)
            self._apply_project_data(project_data, file_path)
            self.logger.info(f"Project opened successfully: {os.path.basename(file_path)}")
            return True
            
        except (ProjectFileError, ProjectDataError) as e:
            self.logger.error(f"Failed to open project: {e}")
            ErrorHandler.handle_exception(e, self)
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error opening project: {e}")
            ErrorHandler.handle_exception(ProjectFileError(f"Failed to open project: {e}"), self)
            return False

    def _get_project_file_path(self) -> str:
        """Get project file path from user via file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            'Open Project', 
            '', 
            'PLC Project Files (*.plc);;JSON Files (*.json);;All Files (*)'
        )
        return file_path

    def _load_project_data(self, file_path: str) -> dict:
        """
        Load and validate project data from file
        
        Args:
            file_path: Path to project file
            
        Returns:
            Validated project data
            
        Raises:
            ProjectFileError: If file cannot be read or parsed
            ProjectDataError: If project data structure is invalid
        """
        # Validate file path and readability
        validate_file_path(file_path, check_exists=True, check_readable=True)
        
        # Load and validate JSON
        project_data = validate_json_file(file_path)
        
        # Validate project data structure
        validate_project_data(project_data)
        
        return project_data

    def _apply_project_data(self, project_data: dict, file_path: str):
        """
        Apply loaded project data to the application
        
        Args:
            project_data: Validated project data
            file_path: Path to the project file
        """
        try:
            # Load project data into canvas
            self.canvas.load_project(project_data)
            
            # Load tag configuration if available
            if hasattr(self, 'variable_panel') and 'tags_configuration' in project_data:
                self.variable_panel.load_tag_configuration(project_data['tags_configuration'])
            
            # Update application state
            self.current_project_file = file_path
            self.project_modified = False
            filename = os.path.basename(file_path)
            self.setWindowTitle(f"Embedded PLC Flowchart GUI - {filename}")
            
        except Exception as e:
            raise ProjectDataError(f"Failed to apply project data: {e}")

    @log_method_entry
    def save_project(self):
        """Save the current project with improved error handling"""
        self.logger.info("Saving project")
        
        if self.current_project_file:
            return self._save_to_file(self.current_project_file)
        else:
            return self.save_project_as()

    @log_method_entry
    def save_project_as(self):
        """Save the project with a new filename"""
        self.logger.info("Saving project as new file")
        
        file_path = self._get_save_file_path()
        if not file_path:
            return False
        
        return self._save_to_file(file_path)

    def _get_save_file_path(self) -> str:
        """Get save file path from user via file dialog"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            'Save Project As', 
            '', 
            'PLC Project Files (*.plc);;JSON Files (*.json);;All Files (*)'
        )
        return file_path

    def _save_to_file(self, file_path: str) -> bool:
        """
        Internal method to save project data to file with comprehensive error handling
        
        Args:
            file_path: Path to save the file
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Validate directory exists and is writable
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                raise ProjectFileError(f"Directory does not exist: {directory}")
            
            if directory and not os.access(directory, os.W_OK):
                raise ProjectFileError(f"Directory is not writable: {directory}")
            
            # Prepare project data
            project_data = self._prepare_project_data()
            
            # Save to file with proper encoding and error handling
            self._write_project_file(file_path, project_data)
            
            # Update application state
            self._update_save_state(file_path)
            
            self.logger.info(f"Project saved successfully: {os.path.basename(file_path)}")
            return True
            
        except (ProjectFileError, ProjectDataError) as e:
            self.logger.error(f"Failed to save project: {e}")
            ErrorHandler.handle_exception(e, self)
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error saving project: {e}")
            ErrorHandler.handle_exception(ProjectFileError(f"Failed to save project: {e}"), self)
            return False

    def _prepare_project_data(self) -> dict:
        """
        Prepare project data for saving
        
        Returns:
            Complete project data dictionary
            
        Raises:
            ProjectDataError: If data preparation fails
        """
        try:
            # Get project data from canvas
            project_data = self.canvas.get_project_data()
            
            # Add tag configuration if variable panel exists
            if hasattr(self, 'variable_panel'):
                project_data['tags_configuration'] = self.variable_panel.get_tag_configuration()
            
            # Add metadata
            project_data['metadata'] = {
                'version': '1.0',
                'created_by': 'ESP32 PLC GUI',
                'file_format': 'PLC Project File',
                'description': 'Complete ESP32 PLC project with flowchart logic and tag configuration'
            }
            
            return project_data
            
        except Exception as e:
            raise ProjectDataError(f"Failed to prepare project data: {e}")

    def _write_project_file(self, file_path: str, project_data: dict):
        """
        Write project data to file with proper error handling
        
        Args:
            file_path: Path to write the file
            project_data: Project data to write
            
        Raises:
            ProjectFileError: If file write operation fails
        """
        try:
            # Use context manager for proper file handling
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
                
        except PermissionError:
            raise ProjectFileError(f"Permission denied writing to file: {file_path}")
        except OSError as e:
            raise ProjectFileError(f"OS error writing file {file_path}: {e}")
        except (TypeError, ValueError) as e:
            raise ProjectFileError(f"JSON serialization error: {e}")

    def _update_save_state(self, file_path: str):
        """Update application state after successful save"""
        self.current_project_file = file_path
        self.project_modified = False
        filename = os.path.basename(file_path)
        self.setWindowTitle(f"Embedded PLC Flowchart GUI - {filename}")

    @log_method_entry
    def mark_project_modified(self):
        """Mark the project as modified with logging"""
        if not self.project_modified:
            self.project_modified = True
            title = self.windowTitle()
            if not title.endswith('*'):
                self.setWindowTitle(title + '*')
            self.logger.debug("Project marked as modified")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set global application stylesheet to fix highlighting issues
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
    
    QComboBox {
        selection-background-color: #3daee9;
        selection-color: white;
        background-color: white;
        color: black;
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
    
    QListWidget {
        selection-background-color: #3daee9;
        selection-color: white;
        alternate-background-color: #f0f0f0;
        background-color: white;
        color: black;
    }
    
    QListWidget::item:selected {
        background-color: #3daee9;
        color: white;
    }
    
    QListWidget::item:hover {
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
    app.setStyleSheet(global_style)
    
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

def main():
    """Entry point for console script with comprehensive error handling"""
    logger = get_logger('Main')
    
    try:
        logger.info("Starting ESP32 PLC GUI application")
        
        app = QApplication(sys.argv)
        
        # Set global application stylesheet to fix highlighting issues
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
        
        QComboBox {
            selection-background-color: #3daee9;
            selection-color: white;
            background-color: white;
            color: black;
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
        
        QListWidget {
            selection-background-color: #3daee9;
            selection-color: white;
            alternate-background-color: #f0f0f0;
            background-color: white;
            color: black;
        }
        
        QListWidget::item:selected {
            background-color: #3daee9;
            color: white;
        }
        
        QListWidget::item:hover {
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
        app.setStyleSheet(global_style)
        
        # Create and show main window
        win = MainWindow()
        win.show()
        
        logger.info("Application started successfully")
        
        # Run application event loop
        exit_code = app.exec()
        
        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.critical(f"Critical error in main application: {e}", exc_info=True)
        
        # Try to show error dialog if possible
        try:
            if 'app' in locals():
                ErrorHandler.handle_exception(e)
            else:
                # Fallback if QApplication couldn't be created
                print(f"Critical error: {e}")
        except:
            print(f"Critical error: {e}")
        
        return 1  # Return error exit code

if __name__ == "__main__":
    sys.exit(main())