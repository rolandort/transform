import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import TransFormApp
from utils.icon_utils import set_app_icon

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("TransForm")
    app.setStyle("Fusion")  # Fusion respects system colors
    set_app_icon()
    window = TransFormApp()
    window.show()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
