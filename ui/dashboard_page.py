# ui/dashboard_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt
from database import SessionLocal
from models import Elemento, Entrega, Persona, Devolucion
from utils import calcular_tiempo_transcurrido

class DashboardPage(QWidget):
    def __init__(self, usuario_actual, navigate_to):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.navigate_to = navigate_to
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        
        welcome_layout = QVBoxLayout()
        self.lbl_welcome = QLabel(f"Buenos días, {self.usuario_actual.username.capitalize()}")
        self.lbl_welcome.setStyleSheet("font-size: 26px; font-weight: bold; color: #10213c;")
        subtitle = QLabel("Resumen del estado del inventario de radios — Sede Principal")
        subtitle.setStyleSheet("font-size: 14px; color: #7b8493;")
        welcome_layout.addWidget(self.lbl_welcome)
        welcome_layout.addWidget(subtitle)
        
        header_layout.addLayout(welcome_layout)
        header_layout.addStretch()

        # --- RESTRICCIÓN DE ROLES EN EL DASHBOARD ---
        # El técnico no hace entregas ni devoluciones
        if self.usuario_actual.rol in ['Operativo', 'Admin']:
            btn_devolucion = QPushButton("↺ Registrar Devolución")
            btn_devolucion.setStyleSheet("padding: 10px 15px; border: 1px solid #d5dbe5; border-radius: 4px; background: white; font-weight: bold; color: #172033;")
            btn_devolucion.clicked.connect(lambda: self.navigate_to(3, "Registrar devolución", "btn_devolucion"))
            
            btn_entrega = QPushButton("+ Nueva Entrega")
            btn_entrega.setStyleSheet("padding: 10px 15px; border-radius: 4px; background: #003087; color: white; font-weight: bold;")
            btn_entrega.clicked.connect(lambda: self.navigate_to(2, "Registrar nueva entrega", "btn_entrega"))

            header_layout.addWidget(btn_devolucion)
            header_layout.addWidget(btn_entrega)
            
        layout.addLayout(header_layout)

        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(20)
        layout.addLayout(self.cards_layout)

        group_tabla = QFrame()
        group_tabla.setStyleSheet("background: white; border-radius: 8px; border: 1px solid #e1e5eb;")
        layout_tabla = QVBoxLayout(group_tabla)
        layout_tabla.setContentsMargins(20, 20, 20, 20)

        title_tabla = QLabel("Últimas 5 entregas")
        title_tabla.setStyleSheet("font-size: 16px; font-weight: bold; color: #10213c; border: none; background: transparent;")
        layout_tabla.addWidget(title_tabla)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID RADIO", "PERSONA", "TIEMPO EN PRÉSTAMO", "FECHA", "ACCIÓN"])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setStyleSheet("border: none;")
        
        layout_tabla.addWidget(self.tabla)
        layout.addWidget(group_tabla)

        self.cargar_datos()

    def crear_tarjeta(self, titulo, valor, color, porcentaje):
        card = QFrame()
        card.setStyleSheet(f"background: white; border-radius: 8px; border-top: 4px solid {color}; border-left: 1px solid #e1e5eb; border-right: 1px solid #e1e5eb; border-bottom: 1px solid #e1e5eb;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 12px; font-weight: bold; color: #7b8493; background: transparent; border: none;")
        
        lbl_valor = QLabel(str(valor))
        lbl_valor.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color}; background: transparent; border: none;")
        
        barra = QProgressBar()
        barra.setValue(int(porcentaje))
        barra.setTextVisible(False)
        barra.setFixedHeight(6)
        barra.setStyleSheet(f"QProgressBar {{ background: #f0f2f5; border: none; border-radius: 3px; }} QProgressBar::chunk {{ background: {color}; border-radius: 3px; }}")
        
        lbl_porcentaje = QLabel(f"{porcentaje:.1f}% del inventario total")
        lbl_porcentaje.setStyleSheet(f"font-size: 11px; color: {color}; font-weight: bold; background: transparent; border: none;")

        card_layout.addWidget(lbl_titulo)
        card_layout.addWidget(lbl_valor)
        card_layout.addWidget(barra)
        card_layout.addWidget(lbl_porcentaje)

        return card

    def cargar_datos(self):
        db = SessionLocal()
        try:
            for i in reversed(range(self.cards_layout.count())): 
                self.cards_layout.itemAt(i).widget().setParent(None)

            total = db.query(Elemento).count()
            disponibles = db.query(Elemento).filter(Elemento.estado == 'Disponible').count()
            entregados = db.query(Elemento).filter(Elemento.estado == 'Entregado').count()
            mantenimiento = db.query(Elemento).filter(Elemento.estado == 'Mantenimiento').count()

            pct_disp = (disponibles / total * 100) if total > 0 else 0
            pct_ent = (entregados / total * 100) if total > 0 else 0
            pct_mant = (mantenimiento / total * 100) if total > 0 else 0

            self.cards_layout.addWidget(self.crear_tarjeta("RADIOS DISPONIBLES", disponibles, "#28a745", pct_disp))
            self.cards_layout.addWidget(self.crear_tarjeta("RADIOS ENTREGADOS", entregados, "#fd7e14", pct_ent))
            self.cards_layout.addWidget(self.crear_tarjeta("EN MANTENIMIENTO", mantenimiento, "#dc3545", pct_mant))

            ultimas_entregas = db.query(Entrega).order_by(Entrega.id.desc()).limit(5).all()
            self.tabla.setRowCount(0)
            
            for row_idx, ent in enumerate(ultimas_entregas):
                self.tabla.insertRow(row_idx)
                
                radio = db.query(Elemento).filter(Elemento.id == ent.elemento_id).first()
                self.tabla.setItem(row_idx, 0, QTableWidgetItem(radio.codigo_unico if radio else "N/A"))
                
                persona = db.query(Persona).filter(Persona.id == ent.persona_id).first()
                self.tabla.setItem(row_idx, 1, QTableWidgetItem(persona.nombre if persona else "N/A"))
                
                devolucion = db.query(Devolucion).filter(Devolucion.entrega_id == ent.id).first()
                if devolucion:
                    tiempo_str = calcular_tiempo_transcurrido(ent.fecha_hora, devolucion.fecha_hora) + " (Devuelto)"
                else:
                    tiempo_str = calcular_tiempo_transcurrido(ent.fecha_hora) + " (Activo)"
                    
                self.tabla.setItem(row_idx, 2, QTableWidgetItem(tiempo_str))
                self.tabla.setItem(row_idx, 3, QTableWidgetItem(ent.fecha_hora.strftime('%d/%m/%Y - %H:%M')))
                
                btn_ver = QPushButton("👁")
                btn_ver.setStyleSheet("background: transparent; border: none; font-size: 18px; color: #003087;")
                btn_ver.clicked.connect(lambda checked=False, entrega_id=ent.id: self.mostrar_resumen(entrega_id))
                self.tabla.setCellWidget(row_idx, 4, btn_ver)
                
        finally:
            db.close()

    def mostrar_resumen(self, entrega_id):
        db = SessionLocal()
        try:
            entrega = db.query(Entrega).filter(Entrega.id == entrega_id).first()
            if not entrega: return
            
            persona = db.query(Persona).filter(Persona.id == entrega.persona_id).first()
            elemento = db.query(Elemento).filter(Elemento.id == entrega.elemento_id).first()
            
            devolucion = db.query(Devolucion).filter(Devolucion.entrega_id == entrega.id).first()
            
            if devolucion:
                tiempo = calcular_tiempo_transcurrido(entrega.fecha_hora, devolucion.fecha_hora)
                estado_txt = "✅ DEVUELTO"
            else:
                tiempo = calcular_tiempo_transcurrido(entrega.fecha_hora)
                estado_txt = "⏱ ACTIVO (En préstamo)"

            mensaje = f"📋 RESUMEN DEL PRÉSTAMO\n\n"
            mensaje += f"Estado: {estado_txt}\n"
            mensaje += f"📻 Radio: {elemento.codigo_unico if elemento else 'N/A'}\n"
            mensaje += f"👮 Funcionario: {persona.nombre if persona else 'N/A'}\n"
            mensaje += f"🪪 Documento: {persona.documento if persona else 'N/A'}\n"
            mensaje += f"🏢 Dependencia: {persona.dependencia if persona else 'N/A'}\n"
            mensaje += f"📞 Teléfono: {persona.telefono if persona else 'N/A'}\n\n"
            mensaje += f"🎒 Accesorios: {entrega.accesorios}\n"
            mensaje += f"📅 Fecha entrega: {entrega.fecha_hora.strftime('%d/%m/%Y %H:%M')}\n"
            if devolucion:
                mensaje += f"📥 Fecha devolución: {devolucion.fecha_hora.strftime('%d/%m/%Y %H:%M')}\n"
            mensaje += f"⏱ Duración total: {tiempo}\n\n"
            mensaje += f"📝 Observaciones entrega:\n{entrega.observaciones or 'Ninguna'}"

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Detalles del Préstamo")
            msg_box.setText(mensaje)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.exec()
            
        finally:
            db.close()
            