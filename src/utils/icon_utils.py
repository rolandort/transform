import os
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import QApplication

def set_app_icon():
    """Set the application icon for macOS."""
    app_icon_path = os.path.join('icons', 'app-dark.icns')
    if os.path.exists(app_icon_path):
        app = QApplication.instance()
        app.setWindowIcon(QIcon(app_icon_path))

def load_icon(icon_path):
    """Load and prepare an icon for the application."""
    icon = QImage(icon_path)
    if icon.isNull():
        return QIcon()
    
    # Convert to ARGB format if needed
    if icon.format() != QImage.Format.Format_ARGB32:
        icon = icon.convertToFormat(QImage.Format.Format_ARGB32)
    
    return QIcon(QPixmap.fromImage(icon))
