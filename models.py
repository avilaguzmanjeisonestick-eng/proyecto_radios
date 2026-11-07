# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rol = Column(String, nullable=False) # 'Operativo' (Rol 1) o 'Admin' (Rol 2)
    activo = Column(Boolean, default=True)

class Elemento(Base):
    __tablename__ = 'elementos'
    
    id = Column(Integer, primary_key=True)
    codigo_unico = Column(String, unique=True, nullable=False) # Ej: 205CJDXXX
    estado = Column(String, default='Disponible') # 'Disponible', 'Entregado', 'Mantenimiento', 'Retirado'
    observaciones = Column(String, nullable=True) # Observaciones generales del radio
    
    # Relación: Un elemento tiene muchos movimientos (historial)
    movimientos = relationship("Movimiento", back_populates="elemento")

class Persona(Base):
    __tablename__ = 'personas'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    documento = Column(String, unique=True, nullable=False)
    telefono = Column(String, nullable=True)
    dependencia = Column(String, nullable=True)

class Movimiento(Base):
    """
    Clase base para el historial. 
    Aquí aplicamos HERENCIA en POO: Entrega, Devolucion y Mantenimiento 
    heredarán de esta clase.
    """
    __tablename__ = 'movimientos'
    
    id = Column(Integer, primary_key=True)
    elemento_id = Column(Integer, ForeignKey('elementos.id'), nullable=False)
    usuario_sistema_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False) # Quién operó el sistema
    fecha_hora = Column(DateTime, default=datetime.now)
    observaciones = Column(String, nullable=True)
    tipo_movimiento = Column(String) # Para saber qué clase es ('Entrega', 'Devolucion', etc)

    # Relaciones
    elemento = relationship("Elemento", back_populates="movimientos")
    
    # Configuración para la herencia en SQLAlchemy
    __mapper_args__ = {
        'polymorphic_identity': 'movimiento',
        'polymorphic_on': tipo_movimiento
    }

class Entrega(Movimiento):
    __tablename__ = 'entregas'
    
    id = Column(Integer, ForeignKey('movimientos.id'), primary_key=True)
    persona_id = Column(Integer, ForeignKey('personas.id'), nullable=False)
    accesorios = Column(String, nullable=True) # Ej: "clic y funda"
    
    # Relación con Persona
    persona = relationship("Persona")
    
    __mapper_args__ = {
        'polymorphic_identity': 'entrega',
    }

class Devolucion(Movimiento):
    __tablename__ = 'devoluciones'
    
    id = Column(Integer, ForeignKey('movimientos.id'), primary_key=True)
    entrega_id = Column(Integer, ForeignKey('entregas.id'), nullable=False) # A qué entrega corresponde
    estado_resultante = Column(String, nullable=False) # 'Disponible' o 'Mantenimiento'
    accesorios_devueltos = Column(String, nullable=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'devolucion',
    }

class Mantenimiento(Movimiento):
    __tablename__ = 'mantenimientos'
    
    id = Column(Integer, ForeignKey('movimientos.id'), primary_key=True)
    motivo = Column(String, nullable=False)
    fecha_fin = Column(DateTime, nullable=True)
    usuario_fin_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'mantenimiento',
    }