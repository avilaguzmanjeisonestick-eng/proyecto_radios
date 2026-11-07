# ui/history_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView)
from PySide6.QtCore import Qt
from database import SessionLocal
from models import Movimiento, Usuario, Elemento, Devolucion, Mantenimiento
from utils import calcular_tiempo_transcurrido

class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Historial de Movimientos")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #10213c;")
        layout.addWidget(title)

        search_layout = QHBoxLayout()
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por ID del Radio (Ej: 205CJD5076)")
        self.input_buscar.setStyleSheet("padding: 10px; font-size: 14px;")
        
        btn_buscar = QPushButton("Buscar")
        btn_buscar.setObjectName("primary_btn")
        btn_buscar.clicked.connect(self.cargar_historial)
        
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.setStyleSheet("padding: 10px; border: 1px solid #d5dbe5; border-radius: 4px; background: white;")
        btn_limpiar.clicked.connect(self.limpiar_busqueda)
        
        search_layout.addWidget(self.input_buscar)
        search_layout.addWidget(btn_buscar)
        search_layout.addWidget(btn_limpiar)
        layout.addLayout(search_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha / Hora", "Tipo", "ID Radio", "Usuario Sistema", "Observaciones", "Responsable / Movimiento", "Duración"
        ])
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.tabla)
        self.cargar_historial()

    def limpiar_busqueda(self):
        self.input_buscar.clear()
        self.cargar_historial()

    def cargar_historial(self):
        filtro = self.input_buscar.text().strip()
        db = SessionLocal()
        try:
            query = db.query(Movimiento)
            
            if filtro:
                elemento = db.query(Elemento).filter(Elemento.codigo_unico == filtro).first()
                if elemento:
                    query = query.filter(Movimiento.elemento_id == elemento.id)
                else:
                    self.tabla.setRowCount(0)
                    return

            movimientos = query.order_by(Movimiento.fecha_hora.desc()).all()
            
            self.tabla.setRowCount(0)
            for row_idx, mov in enumerate(movimientos):
                self.tabla.insertRow(row_idx)
                
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(mov.fecha_hora.strftime('%d/%m/%Y %H:%M')))
                
                tipo_item = QTableWidgetItem(mov.tipo_movimiento.capitalize())
                if mov.tipo_movimiento == 'entrega': tipo_item.setForeground(Qt.darkBlue)
                elif mov.tipo_movimiento == 'devolucion': tipo_item.setForeground(Qt.darkGreen)
                elif mov.tipo_movimiento == 'mantenimiento': tipo_item.setForeground(Qt.red)
                self.tabla.setItem(row_idx, 1, tipo_item)
                
                radio_codigo = mov.elemento.codigo_unico if mov.elemento else "N/A"
                self.tabla.setItem(row_idx, 2, QTableWidgetItem(radio_codigo))
                
                usuario = db.query(Usuario).filter(Usuario.id == mov.usuario_sistema_id).first()
                self.tabla.setItem(row_idx, 3, QTableWidgetItem(usuario.username if usuario else "Desconocido"))
                
                self.tabla.setItem(row_idx, 4, QTableWidgetItem(mov.observaciones or ""))
                
                responsable_str = "-"
                if mov.tipo_movimiento == 'entrega':
                    if hasattr(mov, 'persona') and mov.persona:
                        responsable_str = f"Entregado a: {mov.persona.nombre}"
                elif mov.tipo_movimiento == 'devolucion':
                    if usuario:
                        responsable_str = f"Recibido por: {usuario.username}"
                elif mov.tipo_movimiento == 'mantenimiento':
                    if usuario:
                        responsable_str = f"Gestionado por: {usuario.username}"

                self.tabla.setItem(row_idx, 5, QTableWidgetItem(responsable_str))

                duracion_str = "-"
                if mov.tipo_movimiento == 'entrega':
                    dev = db.query(Devolucion).filter(Devolucion.entrega_id == mov.id).first()
                    if dev:
                        duracion_str = calcular_tiempo_transcurrido(mov.fecha_hora, dev.fecha_hora)
                    else:
                        duracion_str = calcular_tiempo_transcurrido(mov.fecha_hora) + " (Activo)"
                
                elif mov.tipo_movimiento == 'mantenimiento':
                    mant = db.query(Mantenimiento).filter(Mantenimiento.id == mov.id).first()
                    if mant and mant.fecha_fin:
                        duracion_str = calcular_tiempo_transcurrido(mov.fecha_hora, mant.fecha_fin)
                    else:
                        duracion_str = calcular_tiempo_transcurrido(mov.fecha_hora) + " (En taller)"
                        
                self.tabla.setItem(row_idx, 6, QTableWidgetItem(duracion_str))
                
        finally:
            db.close()