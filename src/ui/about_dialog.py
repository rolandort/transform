from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from utils.icon_utils import resource_path

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About TransForm")
        self.setFixedSize(290, 300)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(58, 58, 60, 0.8);
                border-radius: 10px;
            }
            QLabel {
                color: white;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 30, 20, 30)
        
        # Add app icon
        icon_label = QLabel()

        icon_pixmap = QIcon(resource_path('icons/app-light.icns')).pixmap(256, 256).scaled(
            200, 200, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            # Qt.TransformationMode.SmoothTransformation
        )
        icon_label.setPixmap(icon_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Add app name
        name_label = QLabel("TransForm")
        name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
                
        # Add description
        description = QLabel(
            "Free transformation & cropping of images\n\n"
            "Version 0.1.0\n\n\n"
            "No rights reserved."
        )
        description.setStyleSheet("font-size: 12px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)


