# reset_db.py
from database import SessionLocal, engine
from models import Usuario, Elemento, Persona, Movimiento, Entrega, Devolucion, Mantenimiento
from sqlalchemy import text  # <-- Importante para ejecutar SQL crudo

def resetear_base_de_datos():
    db = SessionLocal()
    try:
        print("Borrando todos los datos de las tablas...")
        db.query(Devolucion).delete()
        db.query(Mantenimiento).delete()
        db.query(Entrega).delete()
        db.query(Movimiento).delete()
        db.query(Elemento).delete()
        db.query(Persona).delete()
        db.query(Usuario).delete()
        db.commit()

        print("Reiniciando contadores de ID (Autoincremento)...")
        with engine.connect() as conn:
            # Envolvemos el texto en text() para que SQLAlchemy lo ejecute
            conn.execute(text("DELETE FROM sqlite_sequence WHERE name IN ('usuarios', 'elementos', 'personas', 'movimientos', 'entregas', 'devoluciones', 'mantenimientos')"))
            conn.commit()

        print("Creando usuario admin de nuevo...")
        admin = Usuario(username='admin', password_hash='123456', rol='Admin')
        db.add(admin)
        db.commit()

        print("¡Base de datos reseteada con éxito! Ya puedes iniciar la app.")
    except Exception as e:
        db.rollback()
        print(f"Error al resetear: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    resetear_base_de_datos()