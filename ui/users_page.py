# ui/users_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox, QComboBox)
from PySide6.QtCore import Qt
from database import SessionLocal
from models import Usuario
from security import encriptar_password

class UsersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Gestión de Usuarios y Roles")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #10213c;")
        layout.addWidget(title)

        # Formulario de creación
        form_layout = QHBoxLayout()
        
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Nombre de usuario")
        self.input_user.setStyleSheet("padding: 10px;")
        
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Contraseña")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setStyleSheet("padding: 10px;")
        
        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["Operativo", "Admin", "Tecnico"])
        self.combo_rol.setStyleSheet("padding: 10px;")
        
        btn_crear = QPushButton("+ Crear Usuario")
        btn_crear.setObjectName("primary_btn")
        btn_crear.clicked.connect(self.crear_usuario)
        
        form_layout.addWidget(self.input_user)
        form_layout.addWidget(self.input_pass)
        form_layout.addWidget(self.combo_rol)
        form_layout.addWidget(btn_crear)
        layout.addLayout(form_layout)

        # Tabla de usuarios (Ahora con 5 columnas, agregamos Acción)
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Usuario", "Rol", "Estado", "Acción"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.tabla)
        self.cargar_usuarios()

    def crear_usuario(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text().strip()
        rol = self.combo_rol.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Debe llenar todos los campos.")
            return

        db = SessionLocal()
        try:
            existe = db.query(Usuario).filter(Usuario.username == username).first()
            if existe:
                QMessageBox.warning(self, "Error", "Ese usuario ya existe.")
                return
            
            nuevo = Usuario(
                username=username, 
                password_hash=encriptar_password(password),
                rol=rol, 
                activo=True
            )
            db.add(nuevo)
            db.commit()
            QMessageBox.information(self, "Éxito", f"Usuario {username} creado como {rol}.")
            
            self.input_user.clear()
            self.input_pass.clear()
            self.cargar_usuarios()
        finally:
            db.close()

    def cargar_usuarios(self):
        db = SessionLocal()
        try:
            usuarios = db.query(Usuario).all()
            self.tabla.setRowCount(0)
            for row_idx, u in enumerate(usuarios):
                self.tabla.insertRow(row_idx)
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(u.id)))
                self.tabla.setItem(row_idx, 1, QTableWidgetItem(u.username))
                self.tabla.setItem(row_idx, 2, QTableWidgetItem(u.rol))
                
                estado_txt = "Activo" if u.activo else "Inactivo"
                item_estado = QTableWidgetItem(estado_txt)
                if u.activo: item_estado.setForeground(Qt.darkGreen)
                else: item_estado.setForeground(Qt.red)
                self.tabla.setItem(row_idx, 3, item_estado)

                # --- NUEVO BOTÓN DE ACTIVAR/DESACTIVAR ---
                btn_estado = QPushButton("Desactivar" if u.activo else "Activar")
                if u.activo:
                    btn_estado.setStyleSheet("background-color: #dc3545; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
                else:
                    btn_estado.setStyleSheet("background-color: #28a745; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
                
                btn_estado.clicked.connect(lambda checked=False, user_id=u.id: self.cambiar_estado(user_id))
                self.tabla.setCellWidget(row_idx, 4, btn_estado)
                
        finally:
            db.close()

    def cambiar_estado(self, user_id):
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
            if usuario:
                # No permitimos que el admin se desactive a sí mismo para no bloquearse
                if usuario.username == 'admin':
                    QMessageBox.warning(self, "Acción Bloqueada", "Por seguridad, el usuario 'admin' principal no puede ser desactivado.")
                    return

                # Invertimos el estado actual (Si es True pasa a False, y viceversa)
                usuario.activo = not usuario.activo
                db.commit()
                
                accion = "desactivado" if not usuario.activo else "activado"
                QMessageBox.information(self, "Éxito", f"El usuario {usuario.username} ha sido {accion}.")
                self.cargar_usuarios()
        finally:
            db.close()
            