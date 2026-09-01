"""
excepciones.py
Jerarquía de excepciones propias, para reemplazar los `ValueError`/`RuntimeError` genéricos. 
No depende de ningún otro módulo para poder importarse desde cualquier lado.
"""

from __future__ import annotations


# Raíz
class AppError(Exception):
    """Excepción base"""

# Usuarios
class UsuarioError(AppError):
    pass

class ClaustroInvalidoError(UsuarioError):
    """Se intentó crear un UsuarioFinal con un claustro invalido"""

    def __init__(self, claustro: str, claustros_validos):
        self.claustro = claustro
        self.claustros_validos = claustros_validos
        super().__init__(f"Claustro inválido: '{claustro}'. Debe ser uno de {claustros_validos}.")


class EmailYaRegistradoError(UsuarioError):
    """Email ya en uso"""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"El email '{email}' ya está registrado.")


class NombreUsuarioYaExisteError(UsuarioError):
    """Nombre de usuario en uso"""

    def __init__(self, nombre_usuario: str):
        self.nombre_usuario = nombre_usuario
        super().__init__(f"El nombre de usuario '{nombre_usuario}' ya está en uso.")


class ContrasenaNoCoincideError(UsuarioError):
    """La contraseña y repetición diferentes"""

    def __init__(self):
        super().__init__("La contraseña y su repetición no coinciden.")


class UsuarioNoEncontradoError(UsuarioError):
    """No existe ningún usuario con ese id"""

    def __init__(self, id_usuario: int):
        self.id_usuario = id_usuario
        super().__init__(f"No existe un usuario con id {id_usuario}.")


# Reclamos
class ReclamoError(AppError):
    pass


class AutoAdhesionError(ReclamoError):
    """Adheción a un reclamo propio"""

    def __init__(self):
        super().__init__("El usuario creador no puede adherirse a su propio reclamo.")


class AdhesionDuplicadaError(ReclamoError):
    """Usuario ya adherido al reclamo"""

    def __init__(self):
        super().__init__("El usuario ya está adherido a este reclamo.")


class TransicionEstadoInvalidaError(ReclamoError):
    """
    Se intentó pasar un reclamo a EN_PROCESO sin tiempo de resolución válido.
    """

    def __init__(self, dias_resolucion: int | None = None):
        self.dias_resolucion = dias_resolucion
        super().__init__(
            "Al pasar un reclamo a EN_PROCESO se debe asignar un "
            "tiempo de resolución entre 1 y 15 días."
        )


class ReclamoNoEncontradoError(ReclamoError):
    """No existe un reclamo con el id pedido"""

    def __init__(self, id_reclamo: int):
        self.id_reclamo = id_reclamo
        super().__init__(f"No existe un reclamo con id {id_reclamo}.")


# Departamentos
class DepartamentoError(AppError):
    pass


class DepartamentoNoEncontradoError(DepartamentoError):
    """
    No existe un Departamento con ese nombre (el clasificador devolvió 
    una etiqueta inexistente en la db o porque se intentó derivar un 
    reclamo a un departamento inexistente)
    """

    def __init__(self, nombre: str):
        self.nombre = nombre
        super().__init__(f"No existe un departamento con nombre '{nombre}'.")


# Clasificación
class ClasificacionError(AppError):
    pass

class ContenidoVacioError(ClasificacionError):
    """Reclamo con contenido vacío"""

    def __init__(self):
        super().__init__("El contenido del reclamo no puede estar vacío.")


# Informes
class InformeError(AppError):
    pass


class TipoInformeNoSoportadoError(InformeError):
    """Tipo de informe que no disponible"""

    def __init__(self, tipo: str, tipos_disponibles):
        self.tipo = tipo
        self.tipos_disponibles = list(tipos_disponibles)
        formatos = ", ".join(sorted(self.tipos_disponibles))
        super().__init__(f"Tipo de informe no soportado: '{tipo}'. Formatos disponibles: {formatos}.")


class GeneracionInformeError(InformeError):
    """
    Falló la generación del informe por un problema de infraestructura
    """

    def __init__(self, mensaje: str):
        super().__init__(mensaje)

# Persistencia (integridad de datos)
class PersistenciaError(AppError):
    """
    Errores que reflejan un problema de integridad de los datos persistidos, no un error de la app
    """

class RolUsuarioDesconocidoError(PersistenciaError):
    """
    Una fila de la tabla `usuarios` tiene un valor de `rol` que no es
    'usuario_final', 'jefe_departamento' ni 'secretario_tecnico'.
    """

    def __init__(self, rol: str):
        self.rol = rol
        super().__init__(f"Rol de usuario desconocido: {rol!r}")
