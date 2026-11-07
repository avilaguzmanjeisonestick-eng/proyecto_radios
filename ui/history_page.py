# ui/history_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox)
from PySide6.QtCore import Qt
from database import SessionLocal
from models import Movimiento, Usuario, Elemento

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

        # --- BARRA DE BÚSQUEDA ---
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

        # --- TABLA DE HISTORIAL ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha / Hora", "Tipo", "ID Radio", "Usuario Sistema", "Observaciones", "Persona"
        ])
        
        # Ajustar tamaño de columnas
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers) # Solo lectura
        
        layout.addWidget(self.tabla)
        
        # Cargar datos iniciales
        self.cargar_historial()

    def limpiar_busqueda(self):
        self.input_buscar.clear()
        self.cargar_historial()

    def cargar_historial(self):
        filtro = self.input_buscar.text().strip()
        db = SessionLocal()
        try:
            # Consultamos la tabla base Movimiento.
            # Gracias a la herencia, esto trae Entregas, Devoluciones y Mantenimientos.
            query = db.query(Movimiento)
            
            if filtro:
                # Si hay filtro, buscamos el elemento por su código y filtramos los movimientos
                elemento = db.query(Elemento).filter(Elemento.codigo_unico == filtro).first()
                if elemento:
                    query = query.filter(Movimiento.elemento_id == elemento.id)
                else:
                    # Si el código no existe, no mostramos nada
                    self.tabla.setRowCount(0)
                    return

            # Ordenar por fecha descendente (lo más reciente primero)
            movimientos = query.order_by(Movimiento.fecha_hora.desc()).all()
            
            self.tabla.setRowCount(0)
            for row_idx, mov in enumerate(movimientos):
                self.tabla.insertRow(row_idx)
                
                # 1. Fecha y Hora
                fecha_str = mov.fecha_hora.strftime('%d/%m/%Y %H:%M')
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(fecha_str))
                
                # 2. Tipo de Movimiento
                tipo_item = QTableWidgetItem(mov.tipo_movimiento.capitalize())
                if mov.tipo_movimiento == 'entrega':
                    tipo_item.setForeground(Qt.darkBlue)
                elif mov.tipo_movimiento == 'devolucion':
                    tipo_item.setForeground(Qt.darkGreen)
                elif mov.tipo_movimiento == 'mantenimiento':
                    tipo_item.setForeground(Qt.red)
                self.tabla.setItem(row_idx, 1, tipo_item)
                
                # 3. ID del Radio
                # La relación 'elemento' la definimos en models.py
                radio_codigo = mov.elemento.codigo_unico if mov.elemento else "N/A"
                self.tabla.setItem(row_idx, 2, QTableWidgetItem(radio_codigo))
                
                # 4. Usuario del Sistema (quién operó)
                usuario = db.query(Usuario).filter(Usuario.id == mov.usuario_sistema_id).first()
                user_str = usuario.username if usuario else "Desconocido"
                self.tabla.setItem(row_idx, 3, QTableWidgetItem(user_str))
                
                # 5. Observaciones
                self.tabla.setItem(row_idx, 4, QTableWidgetItem(mov.observaciones or ""))
                
                # 6. Persona (Solo aplica para entregas)
                # Verificamos si el movimiento tiene el atributo 'persona' (es decir, si es una Entrega)
                persona_str = "-"
                if hasattr(mov, 'persona') and mov.persona:
                    persona_str = mov.persona.nombre
                self.tabla.setItem(row_idx, 5, QTableWidgetItem(persona_str))
                
        finally:
            db.close()