
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        tag_layout.addWidget(self.variable_panel)
        self.tag_dialog.setSizeGripEnabled(True)
        
        # Connect variable panel signals
        self.variable_panel.tags_modified.connect(self.mark_project_modified)

        def show_tag_dialog():
            # Center the dialog in the main window
            parent_geom = self.geometry()
            dlg_geom = self.tag_dialog.frameGeometry()
            center_point = parent_geom.center()
            dlg_geom.moveCenter(center_point)
            self.tag_dialog.move(dlg_geom.topLeft())
            self.tag_dialog.show()

        tags_btn.clicked.connect(show_tag_dialog)

        # Connect file menu actions
        act_new.triggered.connect(self.new_project)
        act_open.triggered.connect(self.open_project)
        act_save.triggered.connect(self.save_project)
        act_saveas.triggered.connect(self.save_project_as)
        
        # Initialize project state
        self.current_project_file = None
        self.project_modified = False
        
        QTimer.singleShot(0,lambda: self.canvas.ensureVisible(0,0,1,1))

    def show_setup_dialog(self):
        # Pass the variable panel to setup dialog for integration
        variable_panel = getattr(self, 'variable_panel', None)
        dlg = SetupDialog(self, variable_panel)
        dlg.exec()

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

    # File Management Methods
    def new_project(self):
        """Create a new project"""
        if self.project_modified:
            reply = QMessageBox.question(self, 'New Project', 
                                       'Current project has unsaved changes. Continue?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Clear the canvas and reset tags
        self.canvas.clear_canvas()
        
        # Reset the variable panel
        if hasattr(self, 'variable_panel'):
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
        
        self.current_project_file = None
        self.project_modified = False
        self.setWindowTitle("Embedded PLC Flowchart GUI - New Project")
        print("New project created")

    def open_project(self):
        """Open an existing project"""
        if self.project_modified:
            reply = QMessageBox.question(self, 'Open Project', 
                                       'Current project has unsaved changes. Continue?',
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return

        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Project', '', 
                                                 'PLC Project Files (*.plc);;JSON Files (*.json);;All Files (*)')
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    project_data = json.load(f)
                
                # Load project data into canvas
                self.canvas.load_project(project_data)
                
                # Load tag configuration if available
                if hasattr(self, 'variable_panel') and 'tags_configuration' in project_data:
                    self.variable_panel.load_tag_configuration(project_data['tags_configuration'])
                
                self.current_project_file = file_path
                self.project_modified = False
                filename = os.path.basename(file_path)
                self.setWindowTitle(f"Embedded PLC Flowchart GUI - {filename}")
                print(f"Project loaded: {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to open project:\n{str(e)}')

    def save_project(self):
        """Save the current project"""
        if self.current_project_file:
            self._save_to_file(self.current_project_file)
        else:
            self.save_project_as()

    def save_project_as(self):
        """Save the project with a new filename"""
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Project As', '', 
                                                 'PLC Project Files (*.plc);;JSON Files (*.json);;All Files (*)')
        if file_path:
            self._save_to_file(file_path)

    def _save_to_file(self, file_path):
        """Internal method to save project data to file"""
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
            
            with open(file_path, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            self.current_project_file = file_path
            self.project_modified = False
            filename = os.path.basename(file_path)
            self.setWindowTitle(f"Embedded PLC Flowchart GUI - {filename}")
            print(f"Project saved: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save project:\n{str(e)}')

    def mark_project_modified(self):
        """Mark the project as modified"""
        if not self.project_modified:
            self.project_modified = True
            title = self.windowTitle()
            if not title.endswith('*'):
                self.setWindowTitle(title + '*')

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