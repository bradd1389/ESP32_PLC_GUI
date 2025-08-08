from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton

class ProjectPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configure proper styling to fix highlighting issues
        self.setup_styles()
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Solution"))
        self.project_table = QTableWidget(1, 2)
        self.project_table.setHorizontalHeaderLabels(["Name", "# of Subroutines"])
        self.project_table.setItem(0, 0, QTableWidgetItem("vProject31"))
        self.project_table.setItem(0, 1, QTableWidgetItem("0"))
        layout.addWidget(self.project_table)
        self.add_sub_btn = QPushButton("Add Subroutine")
        layout.addWidget(self.add_sub_btn)
        self.setLayout(layout)

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
        """
        self.setStyleSheet(style)
