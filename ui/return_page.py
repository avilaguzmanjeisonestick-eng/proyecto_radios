# ui/return_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QGroupBox, QTextEdit, 
                               QMessageBox, QRadioButton, QButtonGroup, QFrame)
from PySide6.QtCore import Qt
from datetime import datetime
from database import SessionLocal
from models import Elemento, Entrega, Devolucion, Mantenimiento, Persona

class ReturnPage(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.entrega_activa = None
        self.radio_encontrado = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Registrar Devolución")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #10213c;")
        layout.addWidget(title)

        # --- SECCIÓN 1: BUSCAR EQUIPO ---
        group_buscar = QGroupBox("1. Buscar Equipo Entregado")
        group_buscar.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #d5dbe5; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_buscar = QHBoxLayout(group_buscar)
        
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Ingresar ID del radio a devolver")
        self.input_buscar.setStyleSheet("padding: 10px; font-size: 14px;")
        
        btn_buscar = QPushButton("Buscar")
        btn_buscar.setObjectName("primary_btn")
        btn_buscar.clicked.connect(self.buscar_radio)
        
        layout_buscar.addWidget(self.input_buscar)
        layout_buscar.addWidget(btn_buscar)
        layout.addWidget(group_buscar)

        # --- SECCIÓN 2: INFO DE ENTREGA ACTIVA (Oculta por defecto) ---
        self.frame_info = QFrame()
        self.frame_info.setStyleSheet("background-color: #f8f9fa; border: 1px solid #e1e5eb; border-radius: 5px; padding: 15px;")
        self.frame_info.setVisible(False)
        layout_info = QVBoxLayout(self.frame_info)
        
        self.lbl_info_radio = QLabel("Radio: ")
        self.lbl_info_radio.setStyleSheet("font-size: 16px; font-weight: bold; color: #003087;")
        self.lbl_info_persona = QLabel("Responsable: ")
        self.lbl_info_fecha = QLabel("Fecha de entrega: ")
        self.lbl_info_accesorios = QLabel("Accesorios: ")
        
        layout_info.addWidget(self.lbl_info_radio)
        layout_info.addWidget(self.lbl_info_persona)
        layout_info.addWidget(self.lbl_info_fecha)
        layout_info.addWidget(self.lbl_info_accesorios)
        layout.addWidget(self.frame_info)

        # --- SECCIÓN 3: DETALLES DE DEVOLUCIÓN ---
        self.group_devolucion = QGroupBox("2. Detalles de la Devolución")
        self.group_devolucion.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #d5dbe5; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        self.group_devolucion.setVisible(False)
        layout_devolucion = QVBoxLayout(self.group_devolucion)

        # Estado resultante
        layout_estado = QHBoxLayout()
        layout_estado.addWidget(QLabel("Estado del elemento al recibir:"))
        
        self.radio_disponible = QRadioButton("Dejar Disponible")
        self.radio_disponible.setChecked(True)
        self.radio_mantenimiento = QRadioButton("Enviar a Mantenimiento")
        
        grupo_estado = QButtonGroup(self)
        grupo_estado.addButton(self.radio_disponible)
        grupo_estado.addButton(self.radio_mantenimiento)
        
        layout_estado.addWidget(self.radio_disponible)
        layout_estado.addWidget(self.radio_mantenimiento)
        layout_estado.addStretch()
        layout_devolucion.addLayout(layout_estado)

        # Observaciones
        self.input_obs_devolucion = QTextEdit()
        self.input_obs_devolucion.setPlaceholderText("Describa el estado en que se recibe el equipo (Ej: 'Se recibe con la antena averiada')")
        self.input_obs_devolucion.setMaximumHeight(80)
        layout_devolucion.addWidget(QLabel("Observaciones de devolución:"))
        layout_devolucion.addWidget(self.input_obs_devolucion)

        # Motivo de mantenimiento (solo visible si se elige mantenimiento)
        self.input_motivo_mant = QLineEdit()
        self.input_motivo_mant.setPlaceholderText("Motivo del mantenimiento (Requerido si envía a mantenimiento)")
        self.input_motivo_mant.setVisible(False)
        self.radio_mantenimiento.toggled.connect(self.toggle_motivo_mantenimiento)
        layout_devolucion.addWidget(self.input_motivo_mant)

        layout.addWidget(self.group_devolucion)

        # --- BOTÓN FINAL ---
        self.btn_procesar = QPushButton("Procesar Devolución")
        self.btn_procesar.setObjectName("primary_btn")
        self.btn_procesar.setStyleSheet("padding: 12px; font-size: 14px;")
        self.btn_procesar.setVisible(False)
        self.btn_procesar.clicked.connect(self.procesar_devolucion)
        layout.addWidget(self.btn_procesar)
        
        layout.addStretch()

    def toggle_motivo_mantenimiento(self):
        self.input_motivo_mant.setVisible(self.radio_mantenimiento.isChecked())

    def buscar_radio(self):
        codigo = self.input_buscar.text().strip()
        if not codigo:
            QMessageBox.warning(self, "Error", "Ingrese un código para buscar.")
            return

        db = SessionLocal()
        try:
            radio = db.query(Elemento).filter(Elemento.codigo_unico == codigo).first()
            
            if not radio:
                QMessageBox.warning(self, "No encontrado", "El radio no existe en el inventario.")
                self.ocultar_paneles()
                return
            
            if radio.estado != 'Entregado':
                QMessageBox.warning(self, "Error", f"El radio está en estado '{radio.estado}'. Solo se pueden devolver radios 'Entregados'.")
                self.ocultar_paneles()
                return

            # Buscar la entrega activa (la última entrega sin devolución)
            # Buscamos todas las entregas de este radio de la más reciente a la más antigua
            entregas = db.query(Entrega).filter(Entrega.elemento_id == radio.id).order_by(Entrega.id.desc()).all()
            
            entrega_activa = None
            for e in entregas:
                # Verificar si esta entrega ya tiene una devolución asociada
                dev_existente = db.query(Devolucion).filter(Devolucion.entrega_id == e.id).first()
                if not dev_existente:
                    entrega_activa = e
                    break
            
            if not entrega_activa:
                QMessageBox.warning(self, "Error de Consistencia", "El radio dice 'Entregado' pero no tiene una entrega activa registrada. Revise la base de datos.")
                self.ocultar_paneles()
                return

            self.radio_encontrado = radio
            self.entrega_activa = entrega_activa
            persona = db.query(Persona).filter(Persona.id == entrega_activa.persona_id).first()

            # Mostrar información en la pantalla
            self.lbl_info_radio.setText(f"Radio: {radio.codigo_unico}")
            self.lbl_info_persona.setText(f"Responsable: {persona.nombre} (CC: {persona.documento})")
            self.lbl_info_fecha.setText(f"Fecha de entrega: {entrega_activa.fecha_hora.strftime('%d/%m/%Y %H:%M')}")
            self.lbl_info_accesorios.setText(f"Accesorios: {entrega_activa.accesorios}")

            self.frame_info.setVisible(True)
            self.group_devolucion.setVisible(True)
            self.btn_procesar.setVisible(True)
            
            # Limpiar campos de devolución por si se hace una nueva búsqueda
            self.input_obs_devolucion.clear()
            self.input_motivo_mant.clear()
            self.radio_disponible.setChecked(True)

        finally:
            db.close()

    def ocultar_paneles(self):
        self.frame_info.setVisible(False)
        self.group_devolucion.setVisible(False)
        self.btn_procesar.setVisible(False)
        self.radio_encontrado = None
        self.entrega_activa = None

    def procesar_devolucion(self):
        if not self.radio_encontrado or not self.entrega_activa:
            return

        obs = self.input_obs_devolucion.toPlainText().strip()
        if not obs:
            QMessageBox.warning(self, "Faltan datos", "Las observaciones de devolución son obligatorias.")
            return

        enviar_mantenimiento = self.radio_mantenimiento.isChecked()
        motivo = self.input_motivo_mant.text().strip()

        if enviar_mantenimiento and not motivo:
            QMessageBox.warning(self, "Faltan datos", "Debe indicar el motivo del mantenimiento.")
            return

        db = SessionLocal()
        try:
            nuevo_estado = 'Mantenimiento' if enviar_mantenimiento else 'Disponible'
            
            # 1. Registrar la Devolución
            nueva_devolucion = Devolucion(
                elemento_id=self.radio_encontrado.id,
                usuario_sistema_id=self.usuario_actual.id,
                entrega_id=self.entrega_activa.id,
                estado_resultante=nuevo_estado,
                accesorios_devueltos=self.entrega_activa.accesorios, # Asumimos que devuelve lo mismo
                observaciones=obs,
                tipo_movimiento='devolucion'
            )
            db.add(nueva_devolucion)

            # 2. Actualizar estado del radio
            self.radio_encontrado.estado = nuevo_estado

            # 3. Si va a mantenimiento, registrar el movimiento
            if enviar_mantenimiento:
                nuevo_mant = Mantenimiento(
                    elemento_id=self.radio_encontrado.id,
                    usuario_sistema_id=self.usuario_actual.id,
                    motivo=motivo,
                    observaciones=f"Ingreso a mantenimiento por devolución",
                    tipo_movimiento='mantenimiento'
                )
                db.add(nuevo_mant)

            db.commit()
            QMessageBox.information(self, "Éxito", f"Devolución registrada. El radio ahora está en estado: {nuevo_estado}.")
            
            # Limpiar todo
            self.input_buscar.clear()
            self.ocultar_paneles()

        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo registrar la devolución: {e}")
        finally:
            db.close()
            