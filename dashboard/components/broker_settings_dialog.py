from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QDialog, 
                            QFormLayout, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
import logging
import re

class BrokerSettingsDialog(QDialog):
    """
    A dialog for configuring MQTT broker IP settings.
    """
    # Signal emitted when broker settings are saved
    settings_saved = pyqtSignal(str, int)
    
    def __init__(self, parent=None, current_ip="192.168.1.231", current_port=1883):
        super().__init__(parent)
        self.setWindowTitle("Broker IP Settings")
        self.current_ip = current_ip
        self.current_port = current_port
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create form layout for inputs
        self.form_layout = QFormLayout()
        
        # IP Address input
        self.ip_input = QLineEdit(current_ip)
        self.ip_input.setPlaceholderText("e.g., 192.168.1.100")
        self.ip_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 3px;")
        self.form_layout.addRow("Broker IP Address:", self.ip_input)
        
        # Port input
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(current_port)
        self.port_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 3px;")
        self.form_layout.addRow("Port:", self.port_input)
        
        self.layout.addLayout(self.form_layout)
        
        # Add description
        description = QLabel("Enter the MQTT broker IP address and port number")
        description.setStyleSheet("font-size: 12px; color: #666; margin: 10px 0;")
        self.layout.addWidget(description, alignment=Qt.AlignCenter)
        
        # Add buttons
        self.button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("background-color: #6c757d; color: white; padding: 8px 16px;")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)
        
        self.button_layout.addStretch()
        
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet("background-color: #007bff; color: white; padding: 8px 16px;")
        self.save_button.clicked.connect(self.save_settings)
        self.button_layout.addWidget(self.save_button)
        
        self.layout.addLayout(self.button_layout)
        
        # Enable enter key to save
        self.save_button.setDefault(True)
        
    def validate_ip(self, ip):
        """Validate IP address format"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False, "Invalid IP format. Use xxx.xxx.xxx.xxx"
        
        octets = ip.split('.')
        for octet in octets:
            num = int(octet)
            if num < 0 or num > 255:
                return False, f"Invalid octet '{octet}'. Must be 0-255"
        
        return True, "Valid IP"
    
    def save_settings(self):
        """Save broker settings to database"""
        ip_address = self.ip_input.text().strip()
        port = self.port_input.value()
        
        if not ip_address:
            QMessageBox.warning(self, "Invalid Input", "Please enter a broker IP address")
            return
        
        # Validate IP address
        is_valid, message = self.validate_ip(ip_address)
        if not is_valid:
            QMessageBox.warning(self, "Invalid IP Address", message)
            return
        
        # Emit signal with new settings
        self.settings_saved.emit(ip_address, port)
        
        # Show success message
        QMessageBox.information(self, "Success", f"Broker settings saved:\nIP: {ip_address}\nPort: {port}")
        
        # Close dialog
        self.accept()
    
    def get_settings(self):
        """Get current broker settings"""
        return self.ip_input.text().strip(), self.port_input.value()