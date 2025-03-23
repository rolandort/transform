import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import PerspectiveCorrectionApp
from utils.icon_utils import set_app_icon

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("PerspectiveFix")
    set_app_icon()
    window = PerspectiveCorrectionApp()
    window.show()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
