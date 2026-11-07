# ui/main_window.py
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QStackedWidget, QFrame, 
                               QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QTimer
from datetime import datetime
from database import SessionLocal
from models import Elemento
from ui.dialogs import DialogoNuevoRadio

from ui.dashboard_page import DashboardPage
from ui.delivery_page import DeliveryPage
from ui.return_page import ReturnPage
from ui.history_page import HistoryPage
from ui.maintenance_page import MaintenancePage
from ui.users_page import UsersPage

class MainWindow(QMainWindow):
    def __init__(self, usuario_actual, cerrar_sesion_callback):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.cerrar_sesion_callback = cerrar_sesion_callback
        self.rol = usuario_actual.rol
        self.setWindowTitle("MESOAlogin - Gestión de Radios")
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
        
        user_frame = QFrame()
        user_frame.setObjectName("user_frame")
        user_layout = QVBoxLayout(user_frame)
        user_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_user = QLabel(f"👮 {self.usuario_actual.username.upper()}")
        lbl_user.setObjectName("user_label")
        
        lbl_rol = QLabel(f"Rol: {self.rol}")
        lbl_rol.setObjectName("role_label")
        
        user_layout.addWidget(lbl_user)
        user_layout.addWidget(lbl_rol)
        sidebar_layout.addWidget(user_frame)

        # Sección Operación
        lbl_op = QLabel("OPERACIÓN")
        lbl_op.setStyleSheet("color: #7b93b5; font-size: 10px; font-weight: bold; margin-left: 20px; margin-top: 15px; background: transparent;")
        sidebar_layout.addWidget(lbl_op)

        self.btn_dashboard = QPushButton("Inicio")
        self.btn_entrega = QPushButton("Entregas")
        self.btn_devolucion = QPushButton("Devoluciones")
        self.btn_inventario = QPushButton("Inventario")
        self.btn_historial = QPushButton("Historial")
        
        self.btn_dashboard.setProperty("active", "true")

        sidebar_layout.addWidget(self.btn_dashboard)
        
        if self.rol in ['Operativo', 'Admin']:
            sidebar_layout.addWidget(self.btn_entrega)
            sidebar_layout.addWidget(self.btn_devolucion)
            
        sidebar_layout.addWidget(self.btn_inventario)
        sidebar_layout.addWidget(self.btn_historial)
        sidebar_layout.addStretch()

        # --- SECCIÓN SISTEMA ---
        self.btn_mantenimiento = QPushButton("Administración")
        self.btn_usuarios = QPushButton("Usuarios")
        
        if self.rol in ['Admin', 'Tecnico']:
            lbl_sys = QLabel("SISTEMA")
            lbl_sys.setStyleSheet("color: #7b93b5; font-size: 10px; font-weight: bold; margin-left: 20px; margin-top: 10px; background: transparent;")
            sidebar_layout.addWidget(lbl_sys)
            
            sidebar_layout.addWidget(self.btn_mantenimiento)
            sidebar_layout.addWidget(self.btn_usuarios)

        # --- BOTÓN DE CERRAR SESIÓN (Estilo igual a los demás) ---
        self.btn_logout = QPushButton("🚪 Cerrar Sesión")
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #dfff00; 
                color: #334155; 
                text-align: left; 
                padding: 10px 15px; 
                font-size: 14px; 
                border: none; 
                margin: 4px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FFCC33; 
            }
        """)
        self.btn_logout.clicked.connect(self.procesar_logout)
        sidebar_layout.addWidget(self.btn_logout)

        main_layout.addWidget(sidebar)

        # --- ÁREA DE CONTENIDO ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(60)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(30, 0, 30, 0)
        
        self.page_title = QLabel("Inicio")
        self.page_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #172033;")
        topbar_layout.addWidget(self.page_title)
        topbar_layout.addStretch()
        
        # Reloj Dinámico
        self.lbl_fecha = QLabel()
        self.lbl_fecha.setStyleSheet("color: #7b8493; font-size: 12px; margin-right: 15px; font-weight: bold;")
        topbar_layout.addWidget(self.lbl_fecha)
        
        content_layout.addWidget(topbar)

        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        # --- INSTANCIAR LAS PÁGINAS ---
        self.page_inicio = DashboardPage(self.usuario_actual, self.cambiar_pagina_desde_dashboard)
        self.page_inventario = self.create_inventory_page()
        self.page_entrega = DeliveryPage(self.usuario_actual)
        self.page_devolucion = ReturnPage(self.usuario_actual)
        self.page_historial = HistoryPage(self.usuario_actual)
        self.page_mantenimiento = MaintenancePage(self.usuario_actual)
        self.page_usuarios = UsersPage()

        # --- AGREGAR PÁGINAS AL STACK ---
        self.stacked_widget.addWidget(self.page_inicio)         # 0
        self.stacked_widget.addWidget(self.page_inventario)     # 1
        self.stacked_widget.addWidget(self.page_entrega)        # 2
        self.stacked_widget.addWidget(self.page_devolucion)     # 3
        self.stacked_widget.addWidget(self.page_historial)      # 4
        self.stacked_widget.addWidget(self.page_mantenimiento)  # 5
        self.stacked_widget.addWidget(self.page_usuarios)       # 6

        # --- CONEXIONES DE LOS BOTONES ---
        self.btn_dashboard.clicked.connect(lambda: self.cambiar_pagina(0, "Inicio", self.btn_dashboard))
        self.btn_inventario.clicked.connect(lambda: self.cambiar_pagina(1, "Inventario", self.btn_inventario))
        self.btn_historial.clicked.connect(lambda: self.cambiar_pagina(4, "Historial", self.btn_historial))
        
        if self.rol in ['Operativo', 'Admin']:
            self.btn_entrega.clicked.connect(lambda: self.cambiar_pagina(2, "Entregas", self.btn_entrega))
            self.btn_devolucion.clicked.connect(lambda: self.cambiar_pagina(3, "Devoluciones", self.btn_devolucion))
            
        if self.rol in ['Admin', 'Tecnico']:
            self.btn_mantenimiento.clicked.connect(lambda: self.cambiar_pagina(5, "Administración", self.btn_mantenimiento))
            self.btn_usuarios.clicked.connect(lambda: self.cambiar_pagina(6, "Gestión de Usuarios", self.btn_usuarios))

        main_layout.addWidget(content_area)
        self.cargar_tabla_inventario()

        # --- INICIAR EL RELOJ ---
        self.actualizar_reloj()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_reloj)
        self.timer.start(60000)

    def actualizar_reloj(self):
        ahora = datetime.now()
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        
        dia_semana = dias[ahora.weekday()]
        dia = ahora.day
        mes = meses[ahora.month - 1]
        anio = ahora.year
        hora = ahora.strftime("%H:%M")
        
        self.lbl_fecha.setText(f"{dia_semana}, {dia} {mes} {anio} - {hora}")

    def procesar_logout(self):
        self.cerrar_sesion_callback()

    def cambiar_pagina_desde_dashboard(self, index, title, btn_name):
        btn_map = {
            "btn_entrega": self.btn_entrega,
            "btn_devolucion": self.btn_devolucion
        }
        self.cambiar_pagina(index, title, btn_map.get(btn_name))

    def create_inventory_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        
        header_layout = QHBoxLayout()
        title = QLabel("Listado de Radios")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        if self.rol in ['Admin', 'Tecnico']:
            btn_nuevo = QPushButton("+ Agregar Radio")
            btn_nuevo.setObjectName("primary_btn")
            btn_nuevo.clicked.connect(self.abrir_dialogo_nuevo)
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
                if elem.estado == 'Disponible': item_estado.setForeground(Qt.darkGreen)
                elif elem.estado == 'Entregado': item_estado.setForeground(Qt.darkYellow)
                elif elem.estado == 'Mantenimiento': item_estado.setForeground(Qt.red)
                self.tabla.setItem(row_idx, 1, item_estado)
                self.tabla.setItem(row_idx, 2, QTableWidgetItem(elem.observaciones or ""))
        finally:
            db.close()

    def cambiar_pagina(self, index, title, active_btn):
        self.stacked_widget.setCurrentIndex(index)
        self.page_title.setText(title)
        
        if active_btn is None: return

        botones = [self.btn_dashboard, self.btn_inventario, self.btn_entrega, 
                   self.btn_devolucion, self.btn_historial, self.btn_mantenimiento, self.btn_usuarios]
                   
        for btn in botones:
            if btn.isVisible():
                btn.setProperty("active", "false")
                btn.style().unpolish(btn)
                btn.style().polish(btn)
        
        if active_btn.isVisible():
            active_btn.setProperty("active", "true")
            active_btn.style().unpolish(active_btn)
            active_btn.style().polish(active_btn)

        if index == 0:
            self.page_inicio.cargar_datos()
        elif index == 1:
            self.cargar_tabla_inventario()
        elif index == 4:
            self.page_historial.cargar_historial()
        elif index == 5:
            self.page_mantenimiento.cargar_tabla_mantenimiento()
        elif index == 6:
            self.page_usuarios.cargar_usuarios()