from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from flask import abort

# Clases de dominio y roles
from modules.usuarios import Usuario
from modules.usuarios import JefeDepartamento, SecretarioTecnico

# Flask-Login necesita que la clase de usuario herede de 'UserMixin'.
# Para no modificar nuestra clase de dominio 'Usuario' creamos esta clase "envoltorio".

class UsuarioLogin(UserMixin):
    """Clase envoltorio para compatibilidad con Flask-Login"""
    def __init__(self, entidad_usuario: Usuario):
        # Almacenamos la entidad de dominio completa
        self.entidad = entidad_usuario
        # Flask-Login espera un atributo 'id' (convertido a string)
        self.id = str(entidad_usuario.id_bd)
        # Guardamos atributos útiles para acceso rápido
        self.nombre = entidad_usuario.nombre
        self.nombre_usuario = entidad_usuario.nombre_usuario
        # 'rol' es el mismo que devuelve la entidad de dominio
        self.rol = entidad_usuario.rol
        self.departamento = None

        if isinstance(entidad_usuario, JefeDepartamento):
            self.departamento = entidad_usuario.departamento_asignado.nombre


class GestorDeLogin:
    """
    Clase que gestiona la sesión de usuario usando Flask-Login.
    """
    def __init__(self, login_manager: LoginManager, repo_usuarios):
        self.__login_manager = login_manager
        self.__repo_usuarios = repo_usuarios
        
        # Configura el 'user_loader' de Flask-Login. Esta función le dice a Flask-Login cómo recargar un usuario desde
        # el ID guardado en la sesión.
        @login_manager.user_loader
        def cargar_usuario_actual(id_usuario_str: str):
            """
            Función obligatoria de Flask-Login. Carga un usuario desde el ID
            almacenado en la sesión.
            """
            try:
                id_usuario_int = int(id_usuario_str)
            except ValueError:
                return None # ID debe ser un número

            entidad = self.__repo_usuarios.obtener_por_id(id_usuario_int)
            
            if entidad:
                return UsuarioLogin(entidad)
            else:
                return None

    @property
    def usuario_actual(self) -> UsuarioLogin | None:
        """Devuelve el objeto UsuarioLogin del usuario conectado"""
        return current_user if current_user.is_authenticated else None

    @property
    def usuario_autenticado(self) -> bool:
        """Devuelve True si el usuario está logueado."""
        return current_user.is_authenticated

    def login(self, entidad_usuario: Usuario):
        """Inicia sesión para un usuario."""
        usuario_wrapper = UsuarioLogin(entidad_usuario)
        login_user(usuario_wrapper)

    def logout(self):
        """Cierra la sesión del usuario."""
        logout_user()

    # Decoradores de permisos: permiten proteger rutas en server.py
    
    def se_requiere_login(self, f):
        """Decorador para vistas que requieren que el usuario esté logueado."""
        return login_required(f)

    def rol_requerido(self, roles_permitidos: list[str]):
        """
        Decorador para vistas que requieren un rol específico (ej. 'jefe').
        """
        def decorador(f):
            @wraps(f)
            def funcion_decorada(*args, **kwargs):
                if not self.usuario_autenticado:
                    # Si no está logueado, Flask-Login lo redirige
                    return self.__login_manager.unauthorized()
                if self.usuario_actual.rol not in roles_permitidos:
                    # Si no tiene el rol le damos un error 403 (Prohibido)
                    abort(403, "No tienes permiso para acceder a esta página.")
                return f(*args, **kwargs)
            return funcion_decorada
        return decorador