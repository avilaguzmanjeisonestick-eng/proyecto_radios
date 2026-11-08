# ui/users_page.py
import os
import shutil
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox, QComboBox, QInputDialog, QFileDialog)
from PySide6.QtCore import Qt
from database import SessionLocal, engine
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

        # Cabecera con título y botón de Backup
        header_layout = QHBoxLayout()
        
        title = QLabel("Gestión de Usuarios y Roles")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #10213c;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # NUEVO BOTÓN DE BACKUP
        btn_backup = QPushButton("💾 Hacer Copia de Seguridad")
        btn_backup.setStyleSheet("""
            QPushButton {
                background-color: #003087; color: white; border-radius: 4px;
                padding: 8px 15px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #00276e; }
        """)
        btn_backup.clicked.connect(self.hacer_backup)
        header_layout.addWidget(btn_backup)
        
        layout.addLayout(header_layout)

        # Formulario de creación
        form_layout = QHBoxLayout()
        
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Nombre de usuario (sin espacios)")
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

        # Tabla de usuarios
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Usuario", "Rol", "Estado", "Acciones", "Acceso"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.tabla)
        self.cargar_usuarios()

    def hacer_backup(self):
        # Obtenemos la ruta exacta de la base de datos
        db_path = engine.url.database
        
        if not os.path.exists(db_path):
            QMessageBox.warning(self, "Error", "No se encontró el archivo de base de datos.")
            return

        # Generamos el nombre sugerido con la fecha y hora
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M")
        nombre_sugerido = f"backup_radios_{fecha_hora}.db"

        # Abrimos el diálogo para que el usuario elija dónde guardarlo
        ruta_guardar, _ = QFileDialog.getSaveFileName(
            self, 
            "Guardar Copia de Seguridad", 
            nombre_sugerido, 
            "Archivos de Base de Datos (*.db)"
        )

        if ruta_guardar:
            try:
                # Copiamos el archivo
                shutil.copy2(db_path, ruta_guardar)
                QMessageBox.information(
                    self, 
                    "Copia Exitosa", 
                    f"La copia de seguridad se ha guardado correctamente en:\n\n{ruta_guardar}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Error", 
                    f"No se pudo guardar la copia de seguridad:\n{e}"
                )

    def crear_usuario(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text().strip()
        rol = self.combo_rol.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Debe llenar todos los campos.")
            return

        if " " in username:
            QMessageBox.warning(self, "Error de Formato", "El nombre de usuario no puede contener espacios.")
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

                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)
                action_layout.setSpacing(5)

                if u.username != 'admin':
                    btn_reset = QPushButton("🔑")
                    btn_reset.setToolTip("Restablecer Contraseña")
                    btn_reset.setStyleSheet("background-color: #f39c12; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
                    btn_reset.clicked.connect(lambda checked=False, user_name=u.username: self.restablecer_password(user_name))
                    action_layout.addWidget(btn_reset)

                    btn_estado = QPushButton("Desactivar" if u.activo else "Activar")
                    if u.activo:
                        btn_estado.setStyleSheet("background-color: #dc3545; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
                    else:
                        btn_estado.setStyleSheet("background-color: #28a745; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
                    btn_estado.clicked.connect(lambda checked=False, user_id=u.id: self.cambiar_estado(user_id))
                    action_layout.addWidget(btn_estado)
                    
                    self.tabla.setCellWidget(row_idx, 4, action_widget)
                else:
                    self.tabla.setItem(row_idx, 4, QTableWidgetItem("Protegido"))
                
        finally:
            db.close()

    def restablecer_password(self, username):
        nueva_pass, ok = QInputDialog.getText(
            self, 
            "Restablecer Contraseña", 
            f"Ingrese la nueva contraseña para '{username}':", 
            QLineEdit.Password
        )
        
        if ok and nueva_pass.strip():
            db = SessionLocal()
            try:
                usuario = db.query(Usuario).filter(Usuario.username == username).first()
                if usuario:
                    usuario.password_hash = encriptar_password(nueva_pass.strip())
                    db.commit()
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        f"Contraseña de '{username}' restablecida.\n\nNueva clave: {nueva_pass.strip()}"
                    )
                    self.cargar_usuarios()
            finally:
                db.close()
        elif ok and not nueva_pass.strip():
            QMessageBox.warning(self, "Error", "La contraseña no puede estar vacía.")

    def cambiar_estado(self, user_id):
        db = SessionLocal()
        try:
            usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
            if usuario:
                usuario.activo = not usuario.activo
                db.commit()
                accion = "desactivado" if not usuario.activo else "activado"
                QMessageBox.information(self, "Éxito", f"El usuario {usuario.username} ha sido {accion}.")
                self.cargar_usuarios()
        finally:
            db.close()