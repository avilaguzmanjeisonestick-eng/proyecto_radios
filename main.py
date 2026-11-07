import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QStackedWidget, QFrame, QMessageBox)
from PySide6.QtCore import Qt

# Importamos nuestras clases de base de datos
from database import SessionLocal
from models import Usuario

# --- ESTILOS (QSS - El CSS de PySide6) ---
STYLESHEET = """
QWidget {
    background-color: #f3f5f8;
    font-family: "Segoe UI", Arial, sans-serif;
    color: #172033;
}
/* Estilos del Login */
#login_bg {
    background-color: #003087; 
}
#login_card {
    background-color: white;
    border-radius: 8px;
    padding: 40px;
}
#login_title {
    font-size: 22px;
    font-weight: bold;
    color: #10213c;
}
#login_btn {
    background-color: #003087;
    color: white;
    border-radius: 4px;
    padding: 12px;
    font-weight: bold;
    font-size: 14px;
}
#login_btn:hover {
    background-color: #00276e;
}
QLineEdit {
    padding: 10px;
    border: 1px solid #d5dbe5;
    border-radius: 4px;
    background-color: white;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #003087;
}
/* Estilos del Dashboard */
#sidebar {
    background-color: #003087;
    color: white;
}
#sidebar QPushButton {
    color: #c7d3e7;
    background-color: transparent;
    text-align: left;
    padding: 15px;
    font-size: 14px;
    border: none;
}
#sidebar QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
}
#sidebar QPushButton[active="true"] {
    background-color: rgba(255, 255, 255, 0.15);
    color: white;
    border-left: 4px solid #dfff00;
    font-weight: bold;
}
#topbar {
    background-color: white;
    border-bottom: 1px solid #e1e5eb;
}
#page_title {
    font-size: 18px;
    font-weight: bold;
    color: #172033;
}
"""

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("SECURADIO - Login")
        self.resize(1024, 768)
        self.setObjectName("login_bg")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Tarjeta blanca central
        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedWidth(400)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)

        # Títulos
        title = QLabel("Sistema de Gestión\nde Radios")
        title.setObjectName("login_title")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Ingrese sus credenciales para continuar")
        subtitle.setStyleSheet("color: #7b8493; font-size: 13px; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)

        # Campos
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ingrese su usuario")
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Ingrese su contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)

        # Botón
        login_btn = QPushButton("Ingresar al sistema")
        login_btn.setObjectName("login_btn")
        login_btn.clicked.connect(self.authenticate)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.pass_input)
        card_layout.addWidget(login_btn)

        layout.addWidget(card)

    def authenticate(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos.")
            return

        # --- CONEXIÓN A LA BASE DE DATOS ---
        db = SessionLocal()
        try:
            user = db.query(Usuario).filter(Usuario.username == username).first()
            
            if user and user.password_hash == password:
                if user.activo:
                    self.on_login_success(user)
                    self.close()
                else:
                    QMessageBox.warning(self, "Error", "Usuario inactivo.")
            else:
                QMessageBox.warning(self, "Error", "Credenciales incorrectas.")
        except Exception as e:
            QMessageBox.critical(self, "Error de BD", f"Error de conexión: {e}")
        finally:
            db.close()


class MainWindow(QMainWindow):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.setWindowTitle("SECURADIO - Panel de Control")
        self.resize(1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- SIDEBAR ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        logo = QLabel("SECURADIO\nCONTROL DE ACTIVOS")
        logo.setStyleSheet("color: white; font-weight: bold; font-size: 16px; padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.1);")
        logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo)

        self.btn_dashboard = QPushButton("Inicio")
        self.btn_entrega = QPushButton("Entregas")
        self.btn_devolucion = QPushButton("Devoluciones")
        self.btn_historial = QPushButton("Historial")
        
        self.btn_dashboard.setProperty("active", "true")

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_entrega)
        sidebar_layout.addWidget(self.btn_devolucion)
        sidebar_layout.addWidget(self.btn_historial)
        sidebar_layout.addStretch()

        user_info = QLabel(f"Usuario: {self.usuario_actual.username}\nRol: {self.usuario_actual.rol}")
        user_info.setStyleSheet("color: #a8bad6; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1);")
        sidebar_layout.addWidget(user_info)

        main_layout.addWidget(sidebar)

        # --- ÁREA DE CONTENIDO (Derecha) ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(70)
        topbar_layout = QHBoxLayout(topbar)
        
        self.page_title = QLabel("Panel de control")
        self.page_title.setObjectName("page_title")
        topbar_layout.addWidget(self.page_title)
        topbar_layout.addStretch()

        status = QLabel("🟢 Sistema operativo")
        status.setStyleSheet("color: #687384; font-size: 12px;")
        topbar_layout.addWidget(status)

        content_layout.addWidget(topbar)

        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        self.page_inicio = self.create_placeholder("Métricas y Tarjetas de Inicio")
        self.page_entrega = self.create_placeholder("Formulario de Entrega")
        self.page_devolucion = self.create_placeholder("Formulario de Devolución")
        self.page_historial = self.create_placeholder("Tabla de Historial")

        self.stacked_widget.addWidget(self.page_inicio)
        self.stacked_widget.addWidget(self.page_entrega)
        self.stacked_widget.addWidget(self.page_devolucion)
        self.stacked_widget.addWidget(self.page_historial)

        self.btn_dashboard.clicked.connect(lambda: self.cambiar_pagina(0, "Panel de control", self.btn_dashboard))
        self.btn_entrega.clicked.connect(lambda: self.cambiar_pagina(1, "Registrar nueva entrega", self.btn_entrega))
        self.btn_devolucion.clicked.connect(lambda: self.cambiar_pagina(2, "Registrar devolución", self.btn_devolucion))
        self.btn_historial.clicked.connect(lambda: self.cambiar_pagina(3, "Historial de movimientos", self.btn_historial))

        main_layout.addWidget(content_area)

    def create_placeholder(self, text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 24px; color: #7b8493;")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        return widget

    def cambiar_pagina(self, index, title, active_btn):
        self.stacked_widget.setCurrentIndex(index)
        self.page_title.setText(title)
        
        for btn in [self.btn_dashboard, self.btn_entrega, self.btn_devolucion, self.btn_historial]:
            btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        active_btn.setProperty("active", "true")
        active_btn.style().unpolish(active_btn)
        active_btn.style().polish(active_btn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # <--- ESTA LÍNEA HACE QUE LOS ESTILOS SE VEAN BIEN EN WINDOWS
    app.setStyleSheet(STYLESHEET)

    def login_exitoso(usuario):
        global main_window
        main_window = MainWindow(usuario)
        main_window.show()

    login_window = LoginWindow(login_exitoso)
    login_window.show()

    sys.exit(app.exec())