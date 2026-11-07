# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.styles import STYLESHEET
from ui.login import LoginWindow
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    def login_exitoso(usuario):
        global main_window
        main_window = MainWindow(usuario)
        main_window.show()

    login_window = LoginWindow(login_exitoso)
    login_window.show()

    sys.exit(app.exec())
    