import os
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import QApplication

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def set_app_icon():
    app_icon_path = resource_path('icons/app-light.icns')
    if os.path.exists(app_icon_path):
        app = QApplication.instance()
        app.setWindowIcon(QIcon(app_icon_path))

def load_icon(icon_name):
    icon_path = resource_path(f"icons/{icon_name}")
    icon = QImage(icon_path)
    if icon.isNull():
        return QIcon()
    
    # Convert to ARGB format if needed
    if icon.format() != QImage.Format.Format_ARGB32:
        icon = icon.convertToFormat(QImage.Format.Format_ARGB32)
    
    return QIcon(QPixmap.fromImage(icon))
