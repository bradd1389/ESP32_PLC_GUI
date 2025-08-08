from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout

class CodeBlockEditor(QDialog):
    def __init__(self, initial_code="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Code Block")
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(initial_code)
        layout.addWidget(self.text_edit)
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_code(self):
        return self.text_edit.toPlainText()
