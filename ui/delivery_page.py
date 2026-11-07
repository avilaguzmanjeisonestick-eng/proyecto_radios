# ui/delivery_page.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFormLayout, QGroupBox, 
                               QCheckBox, QTextEdit, QMessageBox, QComboBox)
from PySide6.QtCore import Qt
from database import SessionLocal
from models import Elemento, Persona, Entrega, Usuario

class DeliveryPage(QWidget):
    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual # Guardamos quién está logueado
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Título de la sección
        title = QLabel("Registrar Nueva Entrega")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #10213c;")
        layout.addWidget(title)

        # --- SECCIÓN 1: ID DEL RADIO ---
        group_radio = QGroupBox("1. Identificación del Equipo")
        group_radio.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #d5dbe5; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_radio = QVBoxLayout(group_radio)
        
        self.input_codigo_radio = QLineEdit()
        self.input_codigo_radio.setPlaceholderText("Escanear o ingresar ID del radio (Ej: 205CJD5076)")
        self.input_codigo_radio.setStyleSheet("padding: 12px; font-size: 14px; border: 2px solid #003087; border-radius: 4px;")
        layout_radio.addWidget(self.input_codigo_radio)
        layout.addWidget(group_radio)

        # --- SECCIÓN 2: DATOS DEL FUNCIONARIO ---
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

        # --- SECCIÓN 3: ACCESORIOS Y OBSERVACIONES ---
        group_detalles = QGroupBox("3. Detalles de la Entrega")
        group_detalles.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #d5dbe5; border-radius: 5px; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        layout_detalles = QVBoxLayout(group_detalles)

        # Checkboxes de accesorios
        layout_accesorios = QHBoxLayout()
        self.chk_clic = QCheckBox("Clic")
        self.chk_funda = QCheckBox("Funda")
        self.chk_antena = QCheckBox("Antena")
        self.chk_cargador = QCheckBox("Cargador")
        layout_accesorios.addWidget(self.chk_clic)
        layout_accesorios.addWidget(self.chk_funda)
        layout_accesorios.addWidget(self.chk_antena)
        layout_accesorios.addWidget(self.chk_cargador)
        
        layout_detalles.addWidget(QLabel("Accesorios entregados:"))
        layout_detalles.addLayout(layout_accesorios)

        self.input_observaciones = QTextEdit()
        self.input_observaciones.setPlaceholderText("Escriba aquí cualquier observación relevante (estado del equipo, novedades, etc.)")
        self.input_observaciones.setMaximumHeight(80)
        layout_detalles.addWidget(QLabel("Observaciones:"))
        layout_detalles.addWidget(self.input_observaciones)
        
        layout.addWidget(group_detalles)

        # --- BOTONES DE ACCIÓN ---
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

    def procesar_entrega(self):
        codigo = self.input_codigo_radio.text().strip()
        nombre = self.input_nombre.text().strip()
        cedula = self.input_cedula.text().strip()

        # Validación básica de campos
        if not codigo or not nombre or not cedula:
            QMessageBox.warning(self, "Campos Incompletos", "El código del radio, nombre y cédula son obligatorios.")
            return

        db = SessionLocal()
        try:
            # 1. VALIDACIÓN: ¿El radio existe y está disponible?
            radio = db.query(Elemento).filter(Elemento.codigo_unico == codigo).first()
            if not radio:
                QMessageBox.warning(self, "Error", f"El radio con código '{codigo}' no existe en el inventario.")
                return
            if radio.estado != 'Disponible':
                QMessageBox.warning(self, "Radio No Disponible", f"El radio está actualmente en estado: '{radio.estado}'. No se puede entregar.")
                return

            # 2. Buscar o crear a la persona
            persona = db.query(Persona).filter(Persona.documento == cedula).first()
            if not persona:
                persona = Persona(
                    nombre=nombre,
                    documento=cedula,
                    telefono=self.input_telefono.text().strip(),
                    dependencia=self.combo_dependencia.currentText()
                )
                db.add(persona)
                db.commit() # Guardamos para obtener el ID de la persona
            # 3. VALIDACIÓN: RN-ENT-01 (Máximo 3 radios por persona)
            # Para hacerlo correctamente, buscamos las entregas que esta persona tiene 
            # y que AÚN NO tienen una devolución asociada.
            from models import Devolucion
            
            # Obtenemos todos los IDs de las entregas de esta persona
            entregas_persona = db.query(Entrega.id).filter(Entrega.persona_id == persona.id).all()
            ids_entregas = [e.id for e in entregas_persona]
            
            # Contamos cuántas de esas entregas NO tienen una devolución
            entregas_activas = 0
            if ids_entregas:
                entregas_activas = db.query(Entrega).filter(
                    Entrega.id.in_(ids_entregas),
                    ~Entrega.id.in_(db.query(Devolucion.entrega_id)) # Que NO esté en la tabla devoluciones
                ).count()
            
            if entregas_activas >= 3:
                QMessageBox.warning(self, "Límite Excedido", "Esta persona ya tiene 3 radios asignados (Límite máximo según RN-ENT-01).")
                return

            # 4. Armar el string de accesorios
            accesorios = []
            if self.chk_clic.isChecked(): accesorios.append("Clic")
            if self.chk_funda.isChecked(): accesorios.append("Funda")
            if self.chk_antena.isChecked(): accesorios.append("Antena")
            if self.chk_cargador.isChecked(): accesorios.append("Cargador")
            accesorios_str = ", ".join(accesorios) if accesorios else "Ninguno"

            # 5. Registrar la entrega (Movimiento)
            nueva_entrega = Entrega(
                elemento_id=radio.id,
                usuario_sistema_id=self.usuario_actual.id,
                persona_id=persona.id,
                accesorios=accesorios_str,
                observaciones=self.input_observaciones.toPlainText().strip(),
                tipo_movimiento='entrega'
            )
            db.add(nueva_entrega)

            # 6. Actualizar el estado del radio
            radio.estado = 'Entregado'
            
            db.commit() # Guardar todos los cambios

            QMessageBox.information(self, "Éxito", f"Radio '{codigo}' entregado correctamente a {nombre}.")
            self.limpiar_formulario()

        except Exception as e:
            db.rollback() # Si algo falla, deshacemos los cambios
            QMessageBox.critical(self, "Error de Base de Datos", f"Ocurrió un error al guardar: {e}")
        finally:
            db.close()
            