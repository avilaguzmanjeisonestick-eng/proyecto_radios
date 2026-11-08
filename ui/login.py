# ui/login.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QFont, QPen
from database import SessionLocal
from models import Usuario
from security import verificar_password

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle("MESOAlogin")
        self.resize(1024, 768)

        # --- LAYOUT PRINCIPAL ---
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        layout.setContentsMargins(0, 260, 0, 0) 

        # --- TARJETA DE LOGIN ---
        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedWidth(380)
        card.setStyleSheet("""
            QFrame#login_card {
                background-color: rgba(255, 255, 255, 240); 
                border-radius: 10px;
                padding: 30px;
                border: 1px solid rgba(255, 255, 255, 0.6);
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        title = QLabel("MESOAlogin\nGestión de Radios")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #10213c; margin-bottom: 5px;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Ingrese sus credenciales")
        subtitle.setStyleSheet("color: #7b8493; font-size: 12px; margin-bottom: 15px;")
        subtitle.setAlignment(Qt.AlignCenter)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ingrese su usuario")
        self.user_input.setStyleSheet("padding: 10px; border: 1px solid #cbd5e1; border-radius: 5px; font-size: 13px; background-color: white;")
        
        pass_layout = QHBoxLayout()
        pass_layout.setSpacing(5)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Ingrese su contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet("padding: 10px; border: 1px solid #cbd5e1; border-radius: 5px; font-size: 13px; background-color: white;")
        
        self.btn_ver = QPushButton("👁")
        self.btn_ver.setFixedSize(38, 38)
        self.btn_ver.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        self.btn_ver.clicked.connect(self.toggle_password_visibility)
        
        pass_layout.addWidget(self.pass_input)
        pass_layout.addWidget(self.btn_ver)

        login_btn = QPushButton("Ingresar al sistema")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #dfff00; color: black; border-radius: 5px;
                padding: 12px; font-weight: bold; font-size: 14px; border: none;
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #cbe600; }
        """)
        login_btn.clicked.connect(self.authenticate)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.user_input)
        card_layout.addLayout(pass_layout)
        card_layout.addWidget(login_btn)
        
        layout.addWidget(card)

        # --- TEMPORIZADOR DEL RELOJ ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

    def toggle_password_visibility(self):
        if self.pass_input.echoMode() == QLineEdit.Password:
            self.pass_input.setEchoMode(QLineEdit.Normal)
            self.btn_ver.setText("🙈")
        else:
            self.pass_input.setEchoMode(QLineEdit.Password)
            self.btn_ver.setText("👁")

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

    # --- DISEÑO DEL FONDO (SOLO RADAR Y RELOJ) ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Fondo con degradado radial
        gradient = QRadialGradient(self.rect().center(), self.width() * 0.8)
        gradient.setColorAt(0, QColor("#0a4694"))
        gradient.setColorAt(1, QColor("#001d48"))
        painter.fillRect(self.rect(), gradient)

        # 2. Ondas de radar (Círculos)
        painter.setPen(QPen(QColor(223, 255, 0, 40), 2))
        center = self.rect().center()
        for radius in range(150, max(self.width(), self.height()), 120):
            painter.drawEllipse(center, radius, radius)
            
        # 3. Líneas cruzadas de radar
        painter.setPen(QPen(QColor(40, 167, 69, 30), 2))
        painter.drawLine(0, 0, self.width(), self.height())
        painter.drawLine(0, self.height(), self.width(), 0)

        # --- 4. DIBUJAR EL RELOJ Y LA FECHA ---
        hora_actual = QTime.currentTime().toString("HH:mm:ss")
        fecha_actual = QDate.currentDate().toString("dddd, d 'de' MMMM 'de' yyyy")

        # Hora (arriba)
        font_hora = QFont("Segoe UI", 110, QFont.Bold)
        painter.setFont(font_hora)
        painter.setPen(QColor(255, 255, 255, 45)) 
        painter.drawText(0, 30, self.width(), 150, Qt.AlignHCenter | Qt.AlignTop, hora_actual)

        # Fecha (un poco más abajo)
        font_fecha = QFont("Segoe UI", 24, QFont.Bold)
        painter.setFont(font_fecha)
        painter.setPen(QColor(223, 255, 0, 60)) 
        painter.drawText(0, 185, self.width(), 50, Qt.AlignHCenter | Qt.AlignTop, fecha_actual)