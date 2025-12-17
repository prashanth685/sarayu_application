from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QPushButton, 
                            QMessageBox, QMdiSubWindow, QLabel, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
import logging

class DCSettingsWindow(QMdiSubWindow):
    """
    A subwindow for displaying and editing DC settings for channels.
    """
    # Signal emitted when the window is closed
    closed = pyqtSignal()
    def __init__(self, parent=None, channel_count=4):
        super().__init__(parent)
        self.setWindowTitle("DC Settings")
        self.channel_count = channel_count
        self.setMinimumSize(600, 400)
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        
        # Add title
        title = QLabel("DC Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(title)
        
        # Create table
        self.create_table()
        
        # Add buttons
        self.button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.button_layout.addWidget(self.save_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.close_button)
        
        self.layout.addLayout(self.button_layout)
        
        # Load initial values
        self.load_initial_values()
        
        # Set window flags to make it a proper subwindow
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | 
                           Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
    
    def create_table(self):
        """Create and configure the table widget."""
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Channel, Measured DC, Actual DC
        self.table.setHorizontalHeaderLabels(["Channel", "Measured DC (V)", "Actual DC (V)"])
        
        # Set row count based on channel count
        self.table.setRowCount(self.channel_count)
        
        # Populate channel numbers
        for i in range(self.channel_count):
            # Channel number
            channel_item = QTableWidgetItem(f"Channel {i+1}")
            channel_item.setFlags(channel_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(i, 0, channel_item)
            
            # Measured DC (read-only)
            measured_item = QTableWidgetItem("0.000")
            measured_item.setFlags(measured_item.flags() & ~Qt.ItemIsEditable)
            measured_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 1, measured_item)
            
            # Actual DC (editable)
            actual_item = QTableWidgetItem("0.000")
            actual_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 2, actual_item)
        
        # Configure table properties
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        
        self.layout.addWidget(self.table)
    
    def load_initial_values(self):
        """Load initial DC values (placeholder - implement actual loading logic)"""
        # TODO: Load actual values from settings or database
        pass
    
    def update_measured_dc_values(self, dc_values):
        """Update the measured DC values in the table.
        
        Args:
            dc_values (list): List of DC values to display (up to channel_count values)
        """
        try:
            if not dc_values or not isinstance(dc_values, list):
                return
                
            # Update only the available channels, up to the channel count
            num_values = min(len(dc_values), self.channel_count)
            for i in range(num_values):
                # Format the value with 3 decimal places
                value_str = f"{dc_values[i]:}"
                item = self.table.item(i, 1)  # Column 1 is Measured DC
                if item:
                    item.setText(value_str)
        except Exception as e:
            logging.error(f"Error updating measured DC values: {str(e)}")
    
    def save_settings(self):
        """Save the DC settings."""
        try:
            # TODO: Implement actual saving logic
            # For now, just show a success message
            QMessageBox.information(self, "Success", "DC settings saved successfully!")
        except Exception as e:
            logging.error(f"Error saving DC settings: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to save DC settings: {str(e)}")
    
    def get_dc_values(self):
        """Get the current DC values from the table."""
        values = {}
        for i in range(self.channel_count):
            channel = i + 1
            try:
                measured = float(self.table.item(i, 1).text())
                actual = float(self.table.item(i, 2).text())
                values[channel] = {"measured": measured, "actual": actual}
            except (ValueError, AttributeError) as e:
                logging.error(f"Error reading DC values for channel {channel}: {str(e)}")
        return values
    
    def set_measured_dc(self, channel, value):
        """Set the measured DC value for a channel."""
        if 1 <= channel <= self.channel_count:
            item = self.table.item(channel - 1, 1)
            if item:
                item.setText(f"{value:.3f}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Emit the closed signal before closing
            self.closed.emit()
            super().closeEvent(event)
        except Exception as e:
            logging.error(f"Error during closeEvent: {str(e)}")
            super().closeEvent(event)
