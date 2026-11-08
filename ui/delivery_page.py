# ui/delivery_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFormLayout, QGroupBox, 
                               QCheckBox, QTextEdit, QComboBox)
from PySide6.QtCore import Qt
from database import SessionLocal
from models import Elemento, Persona, Entrega, Devolucion
from ui.dialogs import CustomDialog

class DeliveryPage(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Registrar Nueva Entrega")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #10213c;")
        layout.addWidget(title)

        group_radio = QGroupBox("1. Identificación del Equipo")
        group_radio.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #d5dbe5; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_radio = QVBoxLayout(group_radio)
        
        self.input_codigo_radio = QLineEdit()
        self.input_codigo_radio.setPlaceholderText("Escanear o ingresar ID del radio (Ej: 205CJD5076)")
        self.input_codigo_radio.setStyleSheet("padding: 12px; font-size: 14px; border: 2px solid #003087; border-radius: 4px;")
        layout_radio.addWidget(self.input_codigo_radio)
        layout.addWidget(group_radio)

        group_persona = QGroupBox("2. Datos del Funcionario")
        group_persona.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #d5dbe5; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_persona = QFormLayout(group_persona)
        layout_persona.setSpacing(10)

        self.input_nombre = QLineEdit()
        self.input_cedula = QLineEdit()
        self.input_telefono = QLineEdit()
        self.combo_dependencia = QComboBox()
        self.combo_dependencia.addItems(["Apoyo", "Vigilancia", "Supervisión", "Especialidades", "CAD"])

        layout_persona.addRow("Nombre completo:", self.input_nombre)
        layout_persona.addRow("Cédula:", self.input_cedula)
        layout_persona.addRow("Teléfono:", self.input_telefono)
        layout_persona.addRow("Dependencia:", self.combo_dependencia)
        layout.addWidget(group_persona)

        group_detalles = QGroupBox("3. Detalles de la Entrega")
        group_detalles.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #d5dbe5; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_detalles = QVBoxLayout(group_detalles)

        layout_accesorios = QHBoxLayout()
        self.chk_clic = QCheckBox("Clic")
        self.chk_funda = QCheckBox("Funda")
        self.chk_antena = QCheckBox("Antena")
        self.chk_cargador = QCheckBox("Cargador")
        self.chk_bateria = QCheckBox("Batería")
        
        layout_accesorios.addWidget(self.chk_clic)
        layout_accesorios.addWidget(self.chk_funda)
        layout_accesorios.addWidget(self.chk_antena)
        layout_accesorios.addWidget(self.chk_cargador)
        layout_accesorios.addWidget(self.chk_bateria)
        
        layout_detalles.addWidget(QLabel("Accesorios entregados:"))
        layout_detalles.addLayout(layout_accesorios)

        self.input_observaciones = QTextEdit()
        self.input_observaciones.setPlaceholderText("Escriba aquí cualquier observación relevante...")
        self.input_observaciones.setMaximumHeight(80)
        layout_detalles.addWidget(QLabel("Observaciones:"))
        layout_detalles.addWidget(self.input_observaciones)
        
        layout.addWidget(group_detalles)

        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("padding: 10px 20px; border: 1px solid #d5dbe5; border-radius: 4px; background: white;")
        btn_cancelar.clicked.connect(self.limpiar_formulario)
        
        btn_guardar = QPushButton("Registrar Entrega")
        btn_guardar.setObjectName("primary_btn")
        btn_guardar.setStyleSheet("padding: 10px 30px; font-size: 14px;")
        btn_guardar.clicked.connect(self.procesar_entrega)

        layout_botones.addWidget(btn_cancelar)
        layout_botones.addWidget(btn_guardar)
        layout.addLayout(layout_botones)

    def limpiar_formulario(self):
        self.input_codigo_radio.clear()
        self.input_nombre.clear()
        self.input_cedula.clear()
        self.input_telefono.clear()
        self.input_observaciones.clear()
        self.chk_clic.setChecked(False)
        self.chk_funda.setChecked(False)
        self.chk_antena.setChecked(False)
        self.chk_cargador.setChecked(False)
        self.chk_bateria.setChecked(False)

    def procesar_entrega(self):
        codigo = self.input_codigo_radio.text().strip()
        nombre = self.input_nombre.text().strip()
        cedula = self.input_cedula.text().strip()

        if not codigo or not nombre or not cedula:
            dialog = CustomDialog("Campos Incompletos", "El código del radio, nombre y cédula son obligatorios.", "error", self)
            dialog.exec()
            return

        db = SessionLocal()
        try:
            radio = db.query(Elemento).filter(Elemento.codigo_unico == codigo).first()
            if not radio:
                dialog = CustomDialog("Error de Inventario", f"El radio con código '{codigo}' no existe.", "error", self)
                dialog.exec()
                return
                
            if radio.estado != 'Disponible':
                dialog = CustomDialog("Radio No Disponible", f"El radio está en estado: '{radio.estado}'.\nNo se puede entregar.", "error", self)
                dialog.exec()
                return

            persona = db.query(Persona).filter(Persona.documento == cedula).first()
            if not persona:
                persona = Persona(
                    nombre=nombre, documento=cedula,
                    telefono=self.input_telefono.text().strip(),
                    dependencia=self.combo_dependencia.currentText()
                )
                db.add(persona)
                db.commit()

            entregas_persona = db.query(Entrega.id).filter(Entrega.persona_id == persona.id).all()
            ids_entregas = [e.id for e in entregas_persona]
            entregas_activas = 0
            if ids_entregas:
                entregas_activas = db.query(Entrega).filter(
                    Entrega.id.in_(ids_entregas),
                    ~Entrega.id.in_(db.query(Devolucion.entrega_id))
                ).count()
            
            if entregas_activas >= 3:
                dialog = CustomDialog("Límite Excedido", "Esta persona ya tiene 3 radios asignados.", "error", self)
                dialog.exec()
                return

            accesorios = []
            if self.chk_clic.isChecked(): accesorios.append("Clic")
            if self.chk_funda.isChecked(): accesorios.append("Funda")
            if self.chk_antena.isChecked(): accesorios.append("Antena")
            if self.chk_cargador.isChecked(): accesorios.append("Cargador")
            if self.chk_bateria.isChecked(): accesorios.append("Batería")
            accesorios_str = ", ".join(accesorios) if accesorios else "Ninguno"

            nueva_entrega = Entrega(
                elemento_id=radio.id,
                usuario_sistema_id=self.usuario_actual.id,
                persona_id=persona.id,
                accesorios=accesorios_str,
                observaciones=self.input_observaciones.toPlainText().strip(),
                tipo_movimiento='entrega'
            )
            db.add(nueva_entrega)
            radio.estado = 'Entregado'
            db.commit()
            
            dialog = CustomDialog("Entrega Exitosa", f"El radio '{codigo}' fue entregado correctamente a:\n{nombre}", "exito", self)
            dialog.exec()
            self.limpiar_formulario()

        except Exception as e:
            db.rollback()
            dialog = CustomDialog("Error de Base de Datos", f"Ocurrió un error: {e}", "error", self)
            dialog.exec()
        finally:
            db.close()