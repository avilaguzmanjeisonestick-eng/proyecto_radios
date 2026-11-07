# reparar_db.py
from database import engine, Base, SessionLocal
import models
from models import Usuario

def reconstruir_todo():
    print("1. Destruyendo todas las tablas antiguas...")
    Base.metadata.drop_all(bind=engine)
    
    print("2. Creando las tablas nuevas desde cero...")
    Base.metadata.create_all(bind=engine)
    
    print("3. Creando el usuario administrador...")
    db = SessionLocal()
    try:
        admin = Usuario(username='admin', password_hash='123456', rol='Admin')
        db.add(admin)
        db.commit()
        print("✅ ¡TODO LISTO! Usuario 'admin' con contraseña '123456' creado.")
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reconstruir_todo()
    