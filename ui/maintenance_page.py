# ui/maintenance_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox)
from PySide6.QtCore import Qt
from datetime import datetime
from database import SessionLocal
from models import Elemento, Mantenimiento

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

        # --- TABLA DE MANTENIMIENTO ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID Radio", "Fecha Ingreso", "Motivo", "Acción"])
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.tabla)
        
        # Cargar datos iniciales
        self.cargar_tabla_mantenimiento()

    def cargar_tabla_mantenimiento(self):
        db = SessionLocal()
        try:
            # Buscamos todos los elementos que estén en estado 'Mantenimiento'
            elementos = db.query(Elemento).filter(Elemento.estado == 'Mantenimiento').all()
            self.tabla.setRowCount(0)
            
            for row_idx, elem in enumerate(elementos):
                self.tabla.insertRow(row_idx)
                
                # 1. ID del Radio
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(elem.codigo_unico))
                
                # 2. Buscar el último registro de mantenimiento para este radio
                mant = db.query(Mantenimiento).filter(
                    Mantenimiento.elemento_id == elem.id
                ).order_by(Mantenimiento.id.desc()).first()
                
                fecha_str = mant.fecha_hora.strftime('%d/%m/%Y %H:%M') if mant else "N/A"
                motivo_str = mant.motivo if mant else "No registrado"
                
                self.tabla.setItem(row_idx, 1, QTableWidgetItem(fecha_str))
                self.tabla.setItem(row_idx, 2, QTableWidgetItem(motivo_str))
                
                # 3. Botón de Acción (Finalizar Mantenimiento)
                btn_finalizar = QPushButton("Habilitar Radio")
                btn_finalizar.setStyleSheet("background-color: #2e944b; color: white; border-radius: 4px; padding: 6px;")
                # Usamos una función lambda para pasar el ID del elemento al hacer clic
                btn_finalizar.clicked.connect(lambda checked, e_id=elem.id: self.finalizar_mantenimiento(e_id))
                
                self.tabla.setCellWidget(row_idx, 3, btn_finalizar)
                
        finally:
            db.close()

    def finalizar_mantenimiento(self, elemento_id):
        # Confirmación antes de cambiar el estado
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            "¿Está seguro de que el radio ha sido reparado y está listo para volver a estar Disponible?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.No:
            return

        db = SessionLocal()
        try:
            radio = db.query(Elemento).filter(Elemento.id == elemento_id).first()
            if not radio:
                return

            # 1. Cambiar el estado del radio
            radio.estado = 'Disponible'

            # 2. Actualizar el registro de mantenimiento (fecha de fin y usuario)
            mant = db.query(Mantenimiento).filter(
                Mantenimiento.elemento_id == radio.id
            ).order_by(Mantenimiento.id.desc()).first()
            
            if mant:
                mant.fecha_fin = datetime.now()
                mant.usuario_fin_id = self.usuario_actual.id
                mant.observaciones = f"{mant.observaciones} | Finalizado por {self.usuario_actual.username}"

            db.commit()
            QMessageBox.information(self, "Éxito", f"El radio {radio.codigo_unico} ahora está Disponible.")
            
            # Recargar la tabla para que desaparezca el radio reparado
            self.cargar_tabla_mantenimiento()

        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo finalizar el mantenimiento: {e}")
        finally:
            db.close()