# diagnostico.py
from database import SessionLocal
from models import Elemento, Movimiento, Entrega, Devolucion

db = SessionLocal()
print("=== RADIOS (ELEMENTOS) ===")
for e in db.query(Elemento).all():
    print(f"ID: {e.id} | Código: {e.codigo_unico} | Estado: {e.estado}")

print("\n=== MOVIMIENTOS (TABLA PADRE) ===")
for m in db.query(Movimiento).all():
    print(f"ID: {m.id} | Tipo: {m.tipo_movimiento} | Elemento_ID: {m.elemento_id}")

print("\n=== ENTREGAS (TABLA HIJA) ===")
for en in db.query(Entrega).all():
    print(f"ID: {en.id} | Elemento_ID: {en.elemento_id} | Persona_ID: {en.persona_id}")

print("\n=== DEVOLUCIONES ===")
for d in db.query(Devolucion).all():
    print(f"ID: {d.id} | Entrega_ID: {d.entrega_id} | Elemento_ID: {d.elemento_id}")

db.close()
