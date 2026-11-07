# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Nombre del archivo de la base de datos (se creará solo)
DATABASE_URL = "sqlite:///sistema_radios.db"

# El motor de la base de datos
engine = create_engine(DATABASE_URL, echo=False)

# La clase base de la cual heredarán todos nuestros modelos
Base = declarative_base()

# Fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función de ayuda para obtener la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()