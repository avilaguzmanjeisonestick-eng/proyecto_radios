# utils.py
from datetime import datetime

def calcular_tiempo_transcurrido(fecha_inicio, fecha_fin=None):
    """
    Calcula el tiempo entre dos fechas. Si no hay fecha_fin, usa la fecha actual.
    Retorna un string formateado, ej: "2d 4h 15m"
    """
    if fecha_fin is None:
        fecha_fin = datetime.now()
        
    delta = fecha_fin - fecha_inicio
    dias = delta.days
    horas, remainder = divmod(delta.seconds, 3600)
    minutos, _ = divmod(remainder, 60)
    
    if dias > 0:
        return f"{dias}d {horas}h {minutos}m"
    elif horas > 0:
        return f"{horas}h {minutos}m"
    else:
        return f"{minutos}m"