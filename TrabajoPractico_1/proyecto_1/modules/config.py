# modules/config.py
import os
from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from cachelib.file import FileSystemCache

# CONFIGURACIÓN DE SESIÓN
SESSION_TYPE = 'cachelib'

RUTA_BASE = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
RUTA_CACHE_SESIONES = os.path.join(RUTA_BASE, 'flask_session_cache')

app = Flask("server", static_folder='static', template_folder='templates')

# CARGA DE CONFIGURACIÓN
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# Esta línea carga las variables globales en mayúsculas (ej. SESSION_TYPE) en la configuración de la app.
app.config.from_object(__name__)

app.config["SESSION_CACHELIB"] = FileSystemCache(cache_dir=RUTA_CACHE_SESIONES, threshold=500)
app.config["SESSION_PERMANENT"] = False

# Inicializa la extensión de sesión DESPUÉS de configurar
Session(app)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = "Por favor, inicie sesión para acceder a esta página."
login_manager.login_view = 'login'