# database.py
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Detectamos si estamos en modo desarrollo o en el .exe empaquetado
if getattr(sys, 'frozen', False):
    # Si es un .exe, la base de datos vive en la misma carpeta que el ejecutable
    application_path = os.path.dirname(sys.executable)
else:
    # Si es código Python normal, vive en la carpeta del proyecto
    application_path = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(application_path, "sistema_radios.db")
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()