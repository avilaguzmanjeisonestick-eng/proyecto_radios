# ui/dialogs.py
from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, 
                               QMessageBox, QVBoxLayout, QLabel, QComboBox, QTextEdit, QHBoxLayout)
from database import SessionLocal
from models import Elemento, Mantenimiento
from datetime import datetime

class DialogoNuevoRadio(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Nuevo Elemento")
        self.resize(350, 200)
        
        layout = QFormLayout(self)
        
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Ej: 205CJD5076")
        
        self.input_obs = QLineEdit()
        self.input_obs.setPlaceholderText("Opcional (ej. desgaste carcasa)")
        
        layout.addRow("Código Único:", self.input_codigo)
        layout.addRow("Observaciones:", self.input_obs)
        
        btn_guardar = QPushButton("Guardar Elemento")
        btn_guardar.setObjectName("primary_btn")
        btn_guardar.clicked.connect(self.guardar)
        layout.addRow(btn_guardar)

    def guardar(self):
        codigo = self.input_codigo.text().strip()
        if not codigo:
            QMessageBox.warning(self, "Error", "El código es obligatorio.")
            return
            
        db = SessionLocal()
        try:
            existe = db.query(Elemento).filter(Elemento.codigo_unico == codigo).first()
            if existe:
                QMessageBox.warning(self, "Error", "Ya existe un radio con este código.")
                return
            
            nuevo = Elemento(codigo_unico=codigo, observaciones=self.input_obs.text().strip())
            db.add(nuevo)
            db.commit()
            self.accept() 
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
        finally:
            db.close()

class DialogoBitacoraMantenimiento(QDialog):
    def __init__(self, mantenimiento, parent=None):
        super().__init__(parent)
        self.mantenimiento = mantenimiento
        self.setWindowTitle("Bitácora de Mantenimiento")
        self.resize(450, 350)
        
        layout = QVBoxLayout(self)
        
        lbl_info = QLabel(f"Radio: {mantenimiento.elemento.codigo_unico}\nMotivo de ingreso: {mantenimiento.motivo}")
        lbl_info.setStyleSheet("font-weight: bold; font-size: 14px; color: #003087; margin-bottom: 10px;")
        layout.addWidget(lbl_info)
        
        form = QFormLayout()
        
        self.combo_causa = QComboBox()
        self.combo_causa.addItems([
            "Desgaste natural por uso",
            "Daño por mala manipulación",
            "Golpe o caída accidental",
            "Falla eléctrica / Batería",
            "Pérdida de accesorios",
            "Otro (especificar en bitácora)"
        ])
        form.addRow("Causa de la falla:", self.combo_causa)
        
        layout.addLayout(form)
        
        layout.addWidget(QLabel("Trabajo realizado / Bitácora:"))
        self.text_bitacora = QTextEdit()
        self.text_bitacora.setPlaceholderText("Describa el mantenimiento técnico realizado...")
        
        if self.mantenimiento.observaciones and "Bitácora:" in self.mantenimiento.observaciones:
            partes = self.mantenimiento.observaciones.split("Bitácora:")
            if len(partes) > 1:
                self.text_bitacora.setText(partes[1].strip())
                
        layout.addWidget(self.text_bitacora)
        
        btn_layout = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        
        btn_guardar = QPushButton("Guardar Bitácora")
        btn_guardar.setObjectName("primary_btn")
        btn_guardar.clicked.connect(self.guardar)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_guardar)
        layout.addLayout(btn_layout)

    def guardar(self):
        causa = self.combo_causa.currentText()
        bitacora = self.text_bitacora.toPlainText().strip()
        
        if not bitacora:
            QMessageBox.warning(self, "Faltan datos", "Por favor describa el trabajo realizado en la bitácora.")
            return
            
        db = SessionLocal()
        try:
            mant_db = db.query(Mantenimiento).filter(Mantenimiento.id == self.mantenimiento.id).first()
            if mant_db:
                mant_db.observaciones = f"Causa: {causa} | Bitácora: {bitacora}"
                db.commit()
                self.accept()
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
        finally:
            db.close()
            