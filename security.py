# security.py
import hashlib

def encriptar_password(password):
    """Convierte una contraseña en un hash seguro (SHA-256)."""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_password(password_plana, password_hash):
    """Verifica si la contraseña ingresada coincide con el hash guardado."""
    return encriptar_password(password_plana) == password_hash
