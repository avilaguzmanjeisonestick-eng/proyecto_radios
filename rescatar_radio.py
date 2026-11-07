# rescatar_radio.py
from database import SessionLocal
from models import Elemento, Movimiento, Entrega, Devolucion, Mantenimiento

def rescatar():
    codigo = input("Ingresa el código del radio atascado (Ej: 205CPZ1181): ")
    db = SessionLocal()
    try:
        radio = db.query(Elemento).filter(Elemento.codigo_unico == codigo).first()
        if not radio:
            print("❌ Radio no encontrado.")
            return

        print(f"Radio encontrado: {radio.codigo_unico} (Estado actual: {radio.estado})")
        
        # 1. Borrar movimientos uno por uno (para evitar el error de SQLite)
        devs = db.query(Devolucion).filter(Devolucion.elemento_id == radio.id).all()
        for d in devs:
            db.delete(d)

        mants = db.query(Mantenimiento).filter(Mantenimiento.elemento_id == radio.id).all()
        for m in mants:
            db.delete(m)

        ents = db.query(Entrega).filter(Entrega.elemento_id == radio.id).all()
        for e in ents:
            db.delete(e)

        movs = db.query(Movimiento).filter(Movimiento.elemento_id == radio.id).all()
        for m in movs:
            db.delete(m)

        # 2. Cambiar el estado a Disponible
        radio.estado = 'Disponible'
        
        db.commit()
        print(f"✅ ¡Radio {codigo} reseteado a 'Disponible' y su historial limpiado!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    rescatar()
    