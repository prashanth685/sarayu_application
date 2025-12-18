from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QPushButton, 
                            QMessageBox, QMdiSubWindow, QLabel, QLineEdit, QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
import logging
import json
from datetime import datetime

class DCSettingsWindow(QMdiSubWindow):
    """
    A subwindow for displaying and editing DC settings for channels.
    """
    # Signal emitted when the window is closed
    closed = pyqtSignal()
    def __init__(self, parent=None, channel_count=4, mqtt_handler=None):
        super().__init__(parent)
        self.setWindowTitle("DC Calibration")
        self.channel_count = channel_count
        self.mqtt_handler = mqtt_handler
        self.setMinimumSize(700, 500)
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        
        # Add title
        title = QLabel("DC Calibration")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        self.layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # Add description
        description = QLabel("Enter actual DC values and click 'Send' to calibrate")
        description.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 15px;")
        self.layout.addWidget(description, alignment=Qt.AlignCenter)
        
        # Create table
        self.create_table()
        
        # Add buttons
        self.button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet("background-color: #f0ad4e; color: white; padding: 8px 16px;")
        self.reset_button.clicked.connect(self.reset_values)
        self.button_layout.addWidget(self.reset_button)
        
        self.button_layout.addStretch()
        
        self.send_button = QPushButton("Send Calibration")
        self.send_button.setStyleSheet("background-color: #5cb85c; color: white; font-weight: bold; padding: 8px 16px;")
        self.send_button.clicked.connect(self.send_calibration)
        self.button_layout.addWidget(self.send_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("padding: 8px 16px;")
        self.close_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.close_button)
        
        self.layout.addLayout(self.button_layout)
        
        # Load initial values
        # self.load_initial_values()
        
        # Set window flags to make it a proper subwindow
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | 
                           Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
    
    def create_table(self):
        """Create and configure the table widget."""
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # Channel, Measured DC, Actual DC, Ratio
        self.table.setHorizontalHeaderLabels(["Channel", "Measured DC (V)", "Actual DC (V)", "Calibration Factor"])
        
        # Set row count based on channel count
        self.table.setRowCount(self.channel_count)
        
        # Set column widths
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 150)
        
        # Populate channel numbers
        for i in range(self.channel_count):
            # Channel number
            channel_item = QTableWidgetItem(f"Channel {i+1}")
            channel_item.setFlags(channel_item.flags() & ~Qt.ItemIsEditable)
            channel_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, channel_item)
            
            # Measured DC (read-only)
            measured_item = QTableWidgetItem("0.000")
            measured_item.setFlags(measured_item.flags() & ~Qt.ItemIsEditable)
            measured_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 1, measured_item)
            
            # Actual DC (editable spinbox)
            actual_widget = QWidget()
            actual_layout = QHBoxLayout(actual_widget)
            actual_layout.setContentsMargins(5, 2, 5, 2)
            actual_spinbox = QDoubleSpinBox()
            actual_spinbox.setRange(-1000.0, 1000.0)
            actual_spinbox.setDecimals(3)
            actual_spinbox.setValue(0.0)
            actual_spinbox.setSingleStep(0.1)
            actual_spinbox.valueChanged.connect(self.calculate_ratio)
            actual_layout.addWidget(actual_spinbox)
            actual_layout.setAlignment(Qt.AlignRight)
            self.table.setCellWidget(i, 2, actual_widget)
            
            # Ratio (read-only)
            ratio_item = QTableWidgetItem("1.000")
            ratio_item.setFlags(ratio_item.flags() & ~Qt.ItemIsEditable)
            ratio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 3, ratio_item)
        
        # Configure table properties
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        
        self.layout.addWidget(self.table)
    
    def calculate_ratio(self):
        """Calculate and update the calibration ratio (Actual/Measured)."""
        for i in range(self.channel_count):
            measured_text = self.table.item(i, 1).text()
            try:
                measured = float(measured_text)
                actual = self.table.cellWidget(i, 2).findChild(QDoubleSpinBox).value()
                
                # Avoid division by zero
                if abs(measured) > 1e-9:  # Small threshold to avoid division by very small numbers
                    ratio = actual / measured
                else:
                    ratio = 1.0 if actual == 0 else float('inf')
                
                # Update ratio column
                ratio_item = self.table.item(i, 3)
                if abs(ratio) < 1000:  # Prevent display of very large numbers
                    ratio_item.setText(f"{ratio:.6f}")
                else:
                    ratio_item.setText("N/A")
            except (ValueError, AttributeError) as e:
                logging.error(f"Error calculating ratio: {e}")
    
    def reset_values(self):
        """Reset all input fields to zero."""
        for i in range(self.channel_count):
            spinbox = self.table.cellWidget(i, 2).findChild(QDoubleSpinBox)
            if spinbox:
                spinbox.setValue(0.0)
            self.table.item(i, 3).setText("1.000")
    
    def send_calibration(self):
        """Send calibration data via MQTT."""
        if not self.mqtt_handler:
            QMessageBox.warning(self, "Error", "MQTT handler not available")
            return
        
        try:
            # Create a list to store ratio values
            ratio_values = []
            
            for i in range(self.channel_count):
                # Get the ratio value from the table
                ratio_text = self.table.item(i, 3).text()
                ratio = float(ratio_text) if ratio_text != "N/A" else 1.0
                ratio_values.append(ratio)
            
            # Create a simple dictionary with just the ratio values
            payload = {"calibrated vallues": ratio_values}
            
            # Convert to JSON and publish
            self.mqtt_handler.publish("dccalibrated/data", payload)
            
            QMessageBox.information(self, "Success", "Calibration ratios sent successfully!")
            
        except Exception as e:
            logging.error(f"Error sending calibration data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to send calibration data: {e}")
            
            QMessageBox.information(self, "Success", "Calibration data sent successfully!")
            
        except Exception as e:
            logging.error(f"Error sending calibration data: {e}")
            QMessageBox.critical(self, "Error", f"Failed to send calibration data: {e}")
    
    def update_measured_dc_values(self, dc_values):
        """Update the measured DC values in the table.
        
        Args:
            dc_values (list): List of DC values to display (up to channel_count values)
        """
        if not dc_values or not isinstance(dc_values, list):
            return
            
        try:
            for i, value in enumerate(dc_values[:self.channel_count]):
                try:
                    # Update measured DC value
                    measured_item = self.table.item(i, 1)
                    if measured_item:
                        measured_item.setText(f"{float(value):.3f}")
                    
                    # If actual DC is not set, initialize it with the measured value
                    spinbox = self.table.cellWidget(i, 2).findChild(QDoubleSpinBox)
                    if spinbox and abs(spinbox.value()) < 1e-9:  # Check if close to zero
                        spinbox.setValue(float(value))
                    
                    # Recalculate ratio
                    self.calculate_ratio()
                    
                except (ValueError, AttributeError) as e:
                    logging.error(f"Error updating DC value for channel {i+1}: {e}")
                    
        except Exception as e:
            logging.error(f"Error in update_measured_dc_values: {e}")
            QMessageBox.warning(self, "Error", f"Failed to update DC values: {e}")
    
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
                measured = (self.table.item(i, 1).text())
                actual = (self.table.item(i, 2).text())
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
