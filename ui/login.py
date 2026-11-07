# ui/login.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFrame, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction # <-- Importamos QAction para el ojito
from database import SessionLocal
from models import Usuario
from security import verificar_password

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("CENTINELA - Login")
        self.resize(1024, 768)
        self.setObjectName("login_bg")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedWidth(400)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)

        title = QLabel("Sistema de Gestión\nde Radios")
        title.setObjectName("login_title")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Ingrese sus credenciales para continuar")
        subtitle.setStyleSheet("color: #7b8493; font-size: 13px; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ingrese su usuario")
        
        # --- CAMPO DE CONTRASEÑA CON OJITO ---
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Ingrese su contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        
        # Creamos la acción (el botón dentro del campo)
        self.action_ver = QAction("👁", self.pass_input)
        self.action_ver.triggered.connect(self.toggle_password_visibility)
        # Lo agregamos a la derecha del campo de texto
        self.pass_input.addAction(self.action_ver, QLineEdit.TrailingPosition)

        login_btn = QPushButton("Ingresar al sistema")
        login_btn.setObjectName("login_btn")
        login_btn.clicked.connect(self.authenticate)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.user_input)
        card_layout.addWidget(self.pass_input)
        card_layout.addWidget(login_btn)
        layout.addWidget(card)

    # --- FUNCIÓN PARA MOSTRAR/OCULTAR LA CONTRASEÑA ---
    def toggle_password_visibility(self):
        if self.pass_input.echoMode() == QLineEdit.Password:
            self.pass_input.setEchoMode(QLineEdit.Normal)
            self.action_ver.setText("🙈") # Cambia el icono a un monito tapándose los ojos
        else:
            self.pass_input.setEchoMode(QLineEdit.Password)
            self.action_ver.setText("👁") # Vuelve al ojito

    def authenticate(self):
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos.")
            return

        db = SessionLocal()
        try:
            user = db.query(Usuario).filter(Usuario.username == username).first()
            if user and verificar_password(password, user.password_hash):
                if user.activo:
                    self.on_login_success(user)
                    self.close()
                else:
                    QMessageBox.warning(self, "Error", "Usuario inactivo. Contacte al administrador.")
            else:
                QMessageBox.warning(self, "Error", "Credenciales incorrectas.")
        finally:
            db.close()
            