"""
config_db.py
Configuración mínima de conexión a la base de datos (SQLite). Es infraestructura 
para que main.py pueda crear sesiones de SQLAlchemy sin que el resto del código 
sepa cómo se conecta.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
RUTA_BASE = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
 
URL_BASE_DATOS = os.environ.get("DATABASE_URL")
 
if URL_BASE_DATOS:
    # Algunas plataformas (Heroku y derivados) entregan la URL con el
    # prefijo viejo "postgres://", que SQLAlchemy 1.4+ ya no acepta.
    # Lo normalizamos a "postgresql://" si hace falta.
    if URL_BASE_DATOS.startswith("postgres://"):
        URL_BASE_DATOS = URL_BASE_DATOS.replace("postgres://", "postgresql://", 1)
    _engine = create_engine(URL_BASE_DATOS)
else:
    # Fallback para desarrollo local: SQLite en instance/reclamos.db
    os.makedirs(os.path.join(RUTA_BASE, "instance"), exist_ok=True)
    RUTA_BD = os.path.join(RUTA_BASE, "instance", "reclamos.db")
    _engine = create_engine(f"sqlite:///{RUTA_BD}")
 
_SessionFactory = sessionmaker(bind=_engine)
 
 
def crear_sesion():
    """Devuelve una nueva sesión de SQLAlchemy sobre la BD configurada
    (Postgres en producción vía DATABASE_URL, o SQLite local)."""
    return _SessionFactory()