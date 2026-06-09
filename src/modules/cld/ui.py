from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton


class CloudSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.provider_label = QLabel("Cloud Provider URL:")
        layout.addWidget(self.provider_label)
        self.provider_input = QLineEdit()
        layout.addWidget(self.provider_input)
        self.test_button = QPushButton("Test Connection")
        layout.addWidget(self.test_button)
        self.setLayout(layout)
