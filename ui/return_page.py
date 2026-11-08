# ui/return_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QGroupBox, QTextEdit, 
                               QRadioButton, QButtonGroup, QFrame)
from PySide6.QtCore import Qt
from datetime import datetime
from database import SessionLocal
from models import Elemento, Entrega, Devolucion, Mantenimiento, Persona
from utils import calcular_tiempo_transcurrido
from ui.dialogs import CustomDialog

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

        self.frame_info = QFrame()
        self.frame_info.setStyleSheet("background-color: #f8f9fa; border: 1px solid #e1e5eb; border-radius: 5px; padding: 15px;")
        self.frame_info.setVisible(False)
        layout_info = QVBoxLayout(self.frame_info)
        
        self.lbl_info_radio = QLabel("Radio: ")
        self.lbl_info_radio.setStyleSheet("font-size: 16px; font-weight: bold; color: #003087;")
        self.lbl_info_persona = QLabel("Responsable: ")
        self.lbl_info_fecha = QLabel("Fecha de entrega: ")
        self.lbl_info_accesorios = QLabel("Accesorios: ")
        self.lbl_info_tiempo = QLabel("Tiempo en préstamo: ")
        self.lbl_info_tiempo.setStyleSheet("font-size: 15px; font-weight: bold; color: #d97706; margin-top: 5px;")
        
        layout_info.addWidget(self.lbl_info_radio)
        layout_info.addWidget(self.lbl_info_persona)
        layout_info.addWidget(self.lbl_info_fecha)
        layout_info.addWidget(self.lbl_info_accesorios)
        layout_info.addWidget(self.lbl_info_tiempo)
        layout.addWidget(self.frame_info)

        self.group_devolucion = QGroupBox("2. Detalles de la Devolución")
        self.group_devolucion.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #d5dbe5; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        self.group_devolucion.setVisible(False)
        layout_devolucion = QVBoxLayout(self.group_devolucion)

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

        self.input_obs_devolucion = QTextEdit()
        self.input_obs_devolucion.setPlaceholderText("Describa el estado en que se recibe el equipo")
        self.input_obs_devolucion.setMaximumHeight(80)
        layout_devolucion.addWidget(QLabel("Observaciones de devolución:"))
        layout_devolucion.addWidget(self.input_obs_devolucion)

        self.input_motivo_mant = QLineEdit()
        self.input_motivo_mant.setPlaceholderText("Motivo del mantenimiento")
        self.input_motivo_mant.setVisible(False)
        self.radio_mantenimiento.toggled.connect(self.toggle_motivo_mantenimiento)
        layout_devolucion.addWidget(self.input_motivo_mant)

        layout.addWidget(self.group_devolucion)

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
            dialog = CustomDialog("Faltan datos", "Ingrese un código para buscar.", "error", self)
            dialog.exec()
            return

        db = SessionLocal()
        try:
            radio = db.query(Elemento).filter(Elemento.codigo_unico == codigo).first()
            
            if not radio:
                dialog = CustomDialog("No encontrado", "El radio no existe en el inventario.", "error", self)
                dialog.exec()
                self.ocultar_paneles()
                return
            
            if radio.estado != 'Entregado':
                dialog = CustomDialog("Error", f"El radio está en estado '{radio.estado}'.\nSolo se pueden devolver radios 'Entregados'.", "error", self)
                dialog.exec()
                self.ocultar_paneles()
                return

            entregas = db.query(Entrega).filter(Entrega.elemento_id == radio.id).order_by(Entrega.id.desc()).all()
            
            entrega_activa = None
            for e in entregas:
                dev_existente = db.query(Devolucion).filter(Devolucion.entrega_id == e.id).first()
                if not dev_existente:
                    entrega_activa = e
                    break
            
            if not entrega_activa:
                dialog = CustomDialog("Error de Consistencia", "El radio dice 'Entregado' pero no tiene una entrega activa registrada.", "error", self)
                dialog.exec()
                self.ocultar_paneles()
                return

            self.radio_encontrado = radio
            self.entrega_activa = entrega_activa
            persona = db.query(Persona).filter(Persona.id == entrega_activa.persona_id).first()

            tiempo_str = calcular_tiempo_transcurrido(entrega_activa.fecha_hora)

            self.lbl_info_radio.setText(f"Radio: {radio.codigo_unico}")
            self.lbl_info_persona.setText(f"Responsable: {persona.nombre} (CC: {persona.documento})")
            self.lbl_info_fecha.setText(f"Fecha de entrega: {entrega_activa.fecha_hora.strftime('%d/%m/%Y %H:%M')}")
            self.lbl_info_accesorios.setText(f"Accesorios: {entrega_activa.accesorios}")
            self.lbl_info_tiempo.setText(f"⏱ Tiempo en préstamo: {tiempo_str}")

            self.frame_info.setVisible(True)
            self.group_devolucion.setVisible(True)
            self.btn_procesar.setVisible(True)
            
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
            dialog = CustomDialog("Faltan datos", "Las observaciones de devolución son obligatorias.", "error", self)
            dialog.exec()
            return

        enviar_mantenimiento = self.radio_mantenimiento.isChecked()
        motivo = self.input_motivo_mant.text().strip()

        if enviar_mantenimiento and not motivo:
            dialog = CustomDialog("Faltan datos", "Debe indicar el motivo del mantenimiento.", "error", self)
            dialog.exec()
            return

        db = SessionLocal()
        try:
            nuevo_estado = 'Mantenimiento' if enviar_mantenimiento else 'Disponible'
            
            nueva_devolucion = Devolucion(
                elemento_id=self.radio_encontrado.id,
                usuario_sistema_id=self.usuario_actual.id,
                entrega_id=self.entrega_activa.id,
                estado_resultante=nuevo_estado,
                accesorios_devueltos=self.entrega_activa.accesorios,
                observaciones=obs,
                tipo_movimiento='devolucion'
            )
            db.add(nueva_devolucion)

            radio_db = db.query(Elemento).filter(Elemento.id == self.radio_encontrado.id).first()
            if radio_db:
                radio_db.estado = nuevo_estado

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
            
            dialog = CustomDialog("Devolución Exitosa", f"El radio ahora está en estado:\n{nuevo_estado}", "exito", self)
            dialog.exec()
            
            self.input_buscar.clear()
            self.ocultar_paneles()

        except Exception as e:
            db.rollback()
            dialog = CustomDialog("Error", f"No se pudo registrar la devolución:\n{e}", "error", self)
            dialog.exec()
        finally:
            db.close()