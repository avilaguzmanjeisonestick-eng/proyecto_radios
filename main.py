# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.styles import STYLESHEET
from ui.login import LoginWindow
from ui.main_window import MainWindow

class AppController:
    def __init__(self):
        self.login_window = None
        self.main_window = None

    def iniciar(self):
        self.mostrar_login()

    def mostrar_login(self):
        # Si había una ventana principal abierta, la cerramos
        if self.main_window:
            self.main_window.close()
            self.main_window = None
            
        self.login_window = LoginWindow(self.login_exitoso)
        self.login_window.show()

    def login_exitoso(self, usuario):
        self.login_window.close()
        # Le pasamos la función de cerrar sesión a la ventana principal
        self.main_window = MainWindow(usuario, self.cerrar_sesion)
        self.main_window.show()

    def cerrar_sesion(self):
        self.mostrar_login()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    controller = AppController()
    controller.iniciar()

    sys.exit(app.exec())
    