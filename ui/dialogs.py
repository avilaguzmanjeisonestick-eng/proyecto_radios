# ui/dialogs.py
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox
from database import SessionLocal
from models import Elemento

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