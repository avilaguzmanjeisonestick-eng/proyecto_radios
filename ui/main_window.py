# ui/main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QStackedWidget, QFrame, 
                               QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from database import SessionLocal
from models import Elemento
from ui.dialogs import DialogoNuevoRadio

class MainWindow(QMainWindow):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.setWindowTitle("SECURADIO - Panel de Control")
        self.resize(1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- SIDEBAR ---
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        logo = QLabel("SECURADIO\nCONTROL DE ACTIVOS")
        logo.setStyleSheet("color: white; font-weight: bold; font-size: 16px; padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.1);")
        logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo)

        self.btn_dashboard = QPushButton("Inicio")
        self.btn_inventario = QPushButton("Inventario")
        self.btn_entrega = QPushButton("Entregas")
        self.btn_devolucion = QPushButton("Devoluciones")
        self.btn_historial = QPushButton("Historial")
        
        self.btn_dashboard.setProperty("active", "true")

        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_inventario)
        sidebar_layout.addWidget(self.btn_entrega)
        sidebar_layout.addWidget(self.btn_devolucion)
        sidebar_layout.addWidget(self.btn_historial)
        sidebar_layout.addStretch()

        user_info = QLabel(f"Usuario: {self.usuario_actual.username}\nRol: {self.usuario_actual.rol}")
        user_info.setStyleSheet("color: #a8bad6; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1);")
        sidebar_layout.addWidget(user_info)

        main_layout.addWidget(sidebar)

        # --- ÁREA DE CONTENIDO ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(70)
        topbar_layout = QHBoxLayout(topbar)
        
        self.page_title = QLabel("Panel de control")
        self.page_title.setObjectName("page_title")
        topbar_layout.addWidget(self.page_title)
        topbar_layout.addStretch()
        content_layout.addWidget(topbar)

        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        # Páginas
        self.page_inicio = self.create_placeholder("Métricas y Tarjetas de Inicio")
        self.page_inventario = self.create_inventory_page()
        self.page_entrega = self.create_placeholder("Formulario de Entrega")
        self.page_devolucion = self.create_placeholder("Formulario de Devolución")
        self.page_historial = self.create_placeholder("Tabla de Historial")

        self.stacked_widget.addWidget(self.page_inicio)
        self.stacked_widget.addWidget(self.page_inventario)
        self.stacked_widget.addWidget(self.page_entrega)
        self.stacked_widget.addWidget(self.page_devolucion)
        self.stacked_widget.addWidget(self.page_historial)

        # Conexiones
        self.btn_dashboard.clicked.connect(lambda: self.cambiar_pagina(0, "Panel de control", self.btn_dashboard))
        self.btn_inventario.clicked.connect(lambda: self.cambiar_pagina(1, "Gestión de Inventario", self.btn_inventario))
        self.btn_entrega.clicked.connect(lambda: self.cambiar_pagina(2, "Registrar nueva entrega", self.btn_entrega))
        self.btn_devolucion.clicked.connect(lambda: self.cambiar_pagina(3, "Registrar devolución", self.btn_devolucion))
        self.btn_historial.clicked.connect(lambda: self.cambiar_pagina(4, "Historial de movimientos", self.btn_historial))

        main_layout.addWidget(content_area)
        self.cargar_tabla_inventario()

    def create_placeholder(self, text):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size: 24px; color: #7b8493;")
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        return widget

    def create_inventory_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header_layout = QHBoxLayout()
        title = QLabel("Listado de Radios")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        btn_nuevo = QPushButton("+ Agregar Radio")
        btn_nuevo.setObjectName("primary_btn")
        btn_nuevo.clicked.connect(self.abrir_dialogo_nuevo)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(btn_nuevo)
        layout.addLayout(header_layout)
        
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Código Único", "Estado", "Observaciones"])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        
        layout.addWidget(self.tabla)
        return widget

    def abrir_dialogo_nuevo(self):
        dialogo = DialogoNuevoRadio(self)
        if dialogo.exec():
            self.cargar_tabla_inventario()

    def cargar_tabla_inventario(self):
        db = SessionLocal()
        try:
            elementos = db.query(Elemento).all()
            self.tabla.setRowCount(0)
            
            for row_idx, elem in enumerate(elementos):
                self.tabla.insertRow(row_idx)
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(elem.codigo_unico))
                
                item_estado = QTableWidgetItem(elem.estado)
                if elem.estado == 'Disponible':
                    item_estado.setForeground(Qt.darkGreen)
                elif elem.estado == 'Entregado':
                    item_estado.setForeground(Qt.darkYellow)
                elif elem.estado == 'Mantenimiento':
                    item_estado.setForeground(Qt.red)
                    
                self.tabla.setItem(row_idx, 1, item_estado)
                self.tabla.setItem(row_idx, 2, QTableWidgetItem(elem.observaciones or ""))
        finally:
            db.close()

    def cambiar_pagina(self, index, title, active_btn):
        self.stacked_widget.setCurrentIndex(index)
        self.page_title.setText(title)
        
        for btn in [self.btn_dashboard, self.btn_inventario, self.btn_entrega, self.btn_devolucion, self.btn_historial]:
            btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        active_btn.setProperty("active", "true")
        active_btn.style().unpolish(active_btn)
        active_btn.style().polish(active_btn)