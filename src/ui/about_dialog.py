import os
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About TransForm")
        self.setFixedSize(400, 300)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(28, 28, 30, 0.85);
                border-radius: 10px;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: rgba(44, 44, 46, 0.8);
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(58, 58, 60, 0.8);
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Add app icon
        icon_label = QLabel()

        icon_pixmap = QIcon(os.path.join('icons', 'app-dark.icns')).pixmap(256, 256).scaled(
            128, 128, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            # Qt.TransformationMode.SmoothTransformation
        )
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Add app name
        name_label = QLabel("TransForm")
        name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # Add version
        version_label = QLabel("Version 0.1")
        version_label.setStyleSheet("font-size: 14px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Add description
        description = QLabel(
            "Free transformation and cropping of images.\n\n"
            "No rights reserved."
        )
        description.setStyleSheet("font-size: 14px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
