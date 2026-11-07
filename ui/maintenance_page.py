# ui/maintenance_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox)
from PySide6.QtCore import Qt
from datetime import datetime
from database import SessionLocal
from models import Elemento, Mantenimiento
from utils import calcular_tiempo_transcurrido
from ui.dialogs import DialogoBitacoraMantenimiento

class MaintenancePage(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Gestión de Mantenimiento")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #10213c;")
        layout.addWidget(title)

        subtitle = QLabel("Radios que actualmente se encuentran en revisión técnica.")
        subtitle.setStyleSheet("color: #7b8493; font-size: 14px;")
        layout.addWidget(subtitle)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID Radio", "Fecha Ingreso", "Tiempo en Taller", "Motivo / Causa", "Acciones"])
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.tabla)
        self.cargar_tabla_mantenimiento()

    def cargar_tabla_mantenimiento(self):
        db = SessionLocal()
        try:
            elementos = db.query(Elemento).filter(Elemento.estado == 'Mantenimiento').all()
            self.tabla.setRowCount(0)
            
            for row_idx, elem in enumerate(elementos):
                self.tabla.insertRow(row_idx)
                
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(elem.codigo_unico))
                
                mant = db.query(Mantenimiento).filter(
                    Mantenimiento.elemento_id == elem.id
                ).order_by(Mantenimiento.id.desc()).first()
                
                if mant:
                    fecha_ingreso = mant.fecha_hora.strftime('%d/%m/%Y %H:%M')
                    tiempo_str = calcular_tiempo_transcurrido(mant.fecha_hora)
                    
                    motivo_mostrar = mant.motivo
                    if mant.observaciones and "Causa:" in mant.observaciones:
                        partes = mant.observaciones.split(" | ")
                        if len(partes) > 0:
                            motivo_mostrar += f"\n({partes[0]})"

                    self.tabla.setItem(row_idx, 1, QTableWidgetItem(fecha_ingreso))
                    self.tabla.setItem(row_idx, 2, QTableWidgetItem(tiempo_str))
                    self.tabla.setItem(row_idx, 3, QTableWidgetItem(motivo_mostrar))
                    
                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(0, 0, 0, 0)
                    action_layout.setSpacing(5)
                    
                    btn_ver = QPushButton("👁")
                    btn_ver.setStyleSheet("background: transparent; border: none; font-size: 16px; color: #003087;") # SIN cursor: pointer
                    btn_ver.clicked.connect(lambda checked=False, m_id=mant.id: self.abrir_bitacora(m_id))
                    
                    btn_habilitar = QPushButton("Habilitar")
                    btn_habilitar.setStyleSheet("background-color: #28a745; color: white; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
                    btn_habilitar.clicked.connect(lambda checked=False, m_id=mant.id, e_id=elem.id: self.finalizar_mantenimiento(m_id, e_id))
                    
                    action_layout.addWidget(btn_ver)
                    action_layout.addWidget(btn_habilitar)
                    
                    self.tabla.setCellWidget(row_idx, 4, action_widget)
                
        finally:
            db.close()

    def abrir_bitacora(self, mantenimiento_id):
        db = SessionLocal()
        try:
            mant = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()
            if not mant: return
            
            dialogo = DialogoBitacoraMantenimiento(mant, self)
            if dialogo.exec():
                self.cargar_tabla_mantenimiento()
        finally:
            db.close()

    def finalizar_mantenimiento(self, mantenimiento_id, elemento_id):
        db = SessionLocal()
        try:
            mant = db.query(Mantenimiento).filter(Mantenimiento.id == mantenimiento_id).first()
            
            if not mant.observaciones or "Bitácora:" not in mant.observaciones:
                QMessageBox.warning(self, "Bitácora Requerida", "Debe registrar la bitácora del trabajo realizado antes de habilitar el radio.")
                self.abrir_bitacora(mantenimiento_id)
                return

            respuesta = QMessageBox.question(
                self, "Confirmar", 
                "¿Está seguro de que el radio ha sido reparado y está listo para volver a estar Disponible?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if respuesta == QMessageBox.No:
                return

            radio = db.query(Elemento).filter(Elemento.id == elemento_id).first()
            if not radio: return

            radio.estado = 'Disponible'
            mant.fecha_fin = datetime.now()
            mant.usuario_fin_id = self.usuario_actual.id
            mant.observaciones += f" | Finalizado por: {self.usuario_actual.username}"

            db.commit()
            QMessageBox.information(self, "Éxito", f"El radio {radio.codigo_unico} ahora está Disponible.")
            self.cargar_tabla_mantenimiento()

        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo finalizar: {e}")
        finally:
            db.close()
            