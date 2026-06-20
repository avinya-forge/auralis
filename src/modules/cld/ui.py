"""
Auralis - Cloud UI Module
Implements the Cloud Settings Tab for provider configuration.
"""

from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.modules.cld.test_connection import validate_cloud_endpoint


class CloudSettingsWidget(QWidget):
    """
    UI component for configuring cloud sync providers.
    """

    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI elements."""
        layout = QVBoxLayout(self)

        group_box = QGroupBox("Cloud Provider Configuration")
        form_layout = QFormLayout()

        # Provider Selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["AWS S3", "Google Drive", "Azure Blob"])
        form_layout.addRow(QLabel("Provider:"), self.provider_combo)

        # Credentials
        self.client_id_input = QLineEdit()
        self.client_id_input.setPlaceholderText("Enter Client ID / Access Key")
        form_layout.addRow(QLabel("Client ID:"), self.client_id_input)

        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("Enter Secret Key")
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(QLabel("Secret Key:"), self.secret_key_input)

        # Endpoint URL
        self.endpoint_input = QLineEdit()
        self.endpoint_input.setPlaceholderText("Enter Endpoint URL (e.g. https://api.example.com)")
        form_layout.addRow(QLabel("Endpoint URL:"), self.endpoint_input)

        # Buttons Layout
        button_layout = QVBoxLayout()

        self.test_connection_button = QPushButton("Test Connection")
        self.test_connection_button.clicked.connect(self._on_test_connection)
        button_layout.addWidget(self.test_connection_button)

        self.save_button = QPushButton("Save Configuration")
        self.save_button.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_button)

        group_box.setLayout(form_layout)
        layout.addWidget(group_box)
        layout.addLayout(button_layout)

    def _on_test_connection(self) -> None:
        """Handle test connection action."""
        url = self.endpoint_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Test Connection", "Please enter an endpoint URL.")
            return

        success = validate_cloud_endpoint(url)
        if success:
            QMessageBox.information(self, "Test Connection", "Connection successful!")
        else:
            QMessageBox.critical(
                self, "Test Connection", "Connection failed. Please check the URL and try again."
            )

    def _on_save(self) -> None:
        """Handle save action."""
        _ = self.provider_combo.currentText()
        # In a full implementation, we'd persist these credentials securely.
        pass
