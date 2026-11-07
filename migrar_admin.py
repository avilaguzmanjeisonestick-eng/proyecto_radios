# migrar_admin.py
from database import SessionLocal
from models import Usuario
from security import encriptar_password

db = SessionLocal()
try:
    admin = db.query(Usuario).filter(Usuario.username == 'admin').first()
    if admin:
        admin.password_hash = encriptar_password('123456')
        db.commit()
        print("✅ Contraseña del admin actualizada a formato seguro.")
    else:
        # Si borraste la BD, lo creamos de nuevo
        nuevo = Usuario(username='admin', password_hash=encriptar_password('123456'), rol='Admin')
        db.add(nuevo)
        db.commit()
        print("✅ Usuario admin creado de cero.")
finally:
    db.close()