"""
gestores.py

Agrupa la capa de casos de uso: GestorUsuario y GestorReclamos.

"""

from __future__ import annotations

import os
import uuid
from difflib import SequenceMatcher
from functools import wraps
from typing import Any, Protocol

from flask import abort
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from .usuarios import Usuario, UsuarioFinal, Departamento
from .reclamos import Reclamo, EstadoReclamo
from .dao import DaoUsuarioSQLAlchemy, DaoReclamosSQLAlchemy
from .excepciones import (
    ContrasenaNoCoincideError, EmailYaRegistradoError, NombreUsuarioYaExisteError,
    DepartamentoNoEncontradoError, ImagenNoPermitidaError, ReclamoNoEncontradoError,
    UsuarioNoEncontradoError,
)


class GestorUsuario:
    """
    Casos de uso de usuarios: alta de UsuarioFinal, login/logout y
    control de acceso por rol para los dashboards de jefe de
    departamento / secretario técnico.
    """

    def __init__(self, login_manager: LoginManager, dao_usuarios: DaoUsuarioSQLAlchemy):
        self._login_manager = login_manager
        self._dao_usuarios = dao_usuarios
        # Registra ante Flask-Login cómo recargar un Usuario a partir del
        # id guardado en la sesión (se ejecuta en cada request).
        self._login_manager.user_loader(self._cargar_usuario)

    def _cargar_usuario(self, user_id: str) -> Usuario | None:
        return self._dao_usuarios.obtenerid_usuario(int(user_id))

    # alta de usuario final
    def inscribiruser(self, datos_usuario: dict) -> UsuarioFinal:
        if datos_usuario["contrasena"] != datos_usuario["contrasena_repetida"]:
            raise ContrasenaNoCoincideError()

        if self.filtrarporemail(datos_usuario["email"]) is not None:
            raise EmailYaRegistradoError(datos_usuario["email"])

        if self.filtrarpornombreusuario(datos_usuario["nombre_usuario"]) is not None:
            raise NombreUsuarioYaExisteError(datos_usuario["nombre_usuario"])

        nuevo_usuario = UsuarioFinal(
            nombre=datos_usuario["nombre"],
            apellido=datos_usuario["apellido"],
            email=datos_usuario["email"],
            nombre_usuario=datos_usuario["nombre_usuario"],
            claustro=datos_usuario["claustro"],
            contrasena=datos_usuario["contrasena"],
        )
        return self._dao_usuarios.inscribiruser(nuevo_usuario)

    # consultas
    def filtrarporemail(self, email: str) -> Usuario | None:
        return self._dao_usuarios.filtrarporemail(email)

    def filtrarpornombreusuario(self, nombre_usuario: str) -> Usuario | None:
        return self._dao_usuarios.filtrarpornombreusuario(nombre_usuario)

    def obtenerid_usuario(self, user_id: int) -> Usuario | None:
        return self._dao_usuarios.obtenerid_usuario(user_id)

    def obtener_usu(self) -> list[Usuario]:
        return self._dao_usuarios.obtener_usu()

    # sesión
    def login(self, nombre_usuario: str, contrasena: str) -> Usuario | None:
        """
        Verifica credenciales y inicia sesión con Flask-Login. 
        Devuelve la entidad Usuario logueada, o None si las credenciales son incorrectas
        """
        usuario = self._dao_usuarios.filtrarpornombreusuario(nombre_usuario)
        if usuario is None or not usuario.verificar_contrasena(contrasena):
            return None
        login_user(usuario)
        return usuario

    def logout(self) -> None:
        logout_user()

    # autorización
    def se_requiere_login(self):
        return login_required

    def rol_requerido(self, roles_permitidos: list[str]):
        def decorador(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not current_user.is_authenticated:
                    abort(401)
                if getattr(current_user, "rol", None) not in roles_permitidos:
                    abort(403)
                return func(*args, **kwargs)
            return wrapper
        return decorador


# Contrato del clasificador (GestorReclamos depende de esta forma, no de una clase concreta)
class IClasificadorReclamos(Protocol):
    def clasificar(self, contenido: str) -> str:
        ...


class IAnalitica(Protocol):

    def calculardatos(self, lista_de_reclamos: list) -> Any:
        ...

    def generar_grafica_tor(self, datos: Any) -> str:
        ...

    def generar_grafica_tie(self, datos: Any) -> str:
        ...

    def generar_grafica_pa(self, datos: Any) -> str:
        ...

    def generar_reporte(self, datos: Any, grafico_tor: str, grafico_tie: str,
                         grafico_pa: str, tipo: str) -> Any:
        ...


EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "gif"}


# GestorReclamos
class GestorReclamos:
    """
    Casos de uso de reclamos: creación con clasificación y detección de
    duplicados, adhesión, cambio de estado, derivación entre
    departamentos y consultas para los distintos paneles.
    """

    def __init__(self, dao_usuarios: DaoUsuarioSQLAlchemy,
                 dao_reclamos: DaoReclamosSQLAlchemy,
                 clasificador: IClasificadorReclamos,
                 analitica: IAnalitica):
        self._dao_usuarios = dao_usuarios
        self._dao_reclamos = dao_reclamos
        self._clasificador = clasificador
        self._analitica = analitica

    # adjuntar imagen
    def allowed_file(self, filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS

    def guardar_imagen(self, archivo, subcarpeta: str = "uploads") -> str:
        """
        Guarda la foto adjunta a un reclamo con un nombre único y devuelve la
        ruta RELATIVA A static/, lista para usarse directo como url_for('static', filename=ruta) en los templates
        """
        nombre_seguro = secure_filename(archivo.filename)
        nombre_unico = f"{uuid.uuid4().hex}_{nombre_seguro}"
        carpeta_absoluta = os.path.join("static", subcarpeta)
        os.makedirs(carpeta_absoluta, exist_ok=True)
        archivo.save(os.path.join(carpeta_absoluta, nombre_unico))
        return f"{subcarpeta}/{nombre_unico}"

    # clasificación automática 
    def clasificar_reclamo(self, contenido: str) -> str:
        return self._clasificador.clasificar(contenido)

    # detección de reclamos similares o duplicados
    def comparar(self, contenido_a: str, contenido_b: str, umbral: float = 0.6) -> bool:
        a = " ".join(contenido_a.lower().split())
        b = " ".join(contenido_b.lower().split())
        return SequenceMatcher(None, a, b).ratio() >= umbral

    def buscar_similares(self, nombre_departamento: str, contenido: str) -> list[Reclamo]:
        """
        Busca, entre los reclamos activos del departamento indicado, todos los que tengan contenido
        suficientemente similar al nuevo. Devuelve una lista (puede estar vacía)
        """
        activos = [
            r for r in self._dao_reclamos.get_reclamo_pordepto(nombre_departamento)
            if r.estado in (EstadoReclamo.PENDIENTE, EstadoReclamo.EN_PROCESO)
        ]
        return [r for r in activos if self.comparar(r.contenido, contenido)]
    
    def crear_reclamo(self, datos_reclamo: dict) -> dict:
        contenido = datos_reclamo["contenido"].strip()
        usuario_creador: UsuarioFinal = datos_reclamo["usuario_creador"]

        nombre_departamento = self.clasificar_reclamo(contenido)
        departamento = self._dao_reclamos.obtener_departamento_por_nombre(nombre_departamento)
        if departamento is None:
            raise DepartamentoNoEncontradoError(nombre_departamento)

        imagen = datos_reclamo.get("imagen")
        ruta_imagen = None
        if imagen is not None and getattr(imagen, "filename", ""):
            if not self.allowed_file(imagen.filename):
                raise ImagenNoPermitidaError(imagen.filename)
            ruta_imagen = self.guardar_imagen(imagen)

        similares = self.buscar_similares(departamento.nombre, contenido)
        if similares:
            return {
                "similares": similares, "reclamo": None, "mensaje": None,
                "contenido": contenido, "departamento": departamento,
                "ruta_imagen": ruta_imagen,
            }

        nuevo_reclamo = self.crear_reclamo_forzado(usuario_creador, contenido, departamento, ruta_imagen)
        return {
            "similares": [], "reclamo": nuevo_reclamo, "mensaje": "Reclamo creado",
            "contenido": contenido, "departamento": departamento,
            "ruta_imagen": ruta_imagen,
        }

    def crear_reclamo_forzado(self, usuario_creador: UsuarioFinal, contenido: str,
                               departamento, ruta_imagen: str | None = None) -> Reclamo:
        """
        Uso:
          - crear_reclamo() lo llama cuando no encontró ningún similar.
          - La vista lo llama cuando el usuario tras ver los similares
            que se le mostraron decide que quiere crear el suyo de todas formas
        """
        nuevo_reclamo = Reclamo(usuario_creador=usuario_creador, contenido=contenido,
                                 departamento=departamento, ruta_imagen=ruta_imagen)
        self.guardar_reclamo(nuevo_reclamo)
        return nuevo_reclamo

    def guardar_reclamo(self, reclamo: Reclamo) -> Reclamo:
        return self._dao_reclamos.guardar_reclamo(reclamo)

    def adherirse_reclamo(self, id_reclamo: int, id_usu: int) -> None:
        reclamo = self._dao_reclamos.obtener_por_id(id_reclamo)
        if reclamo is None:
            raise ReclamoNoEncontradoError(id_reclamo)
        usuario = self._dao_usuarios.obtener_por_id(id_usu)
        if usuario is None:
            raise UsuarioNoEncontradoError(id_usu)
        reclamo.agregar_adherente(usuario)  # valida auto-adhesión y duplicados
        self._dao_reclamos.actualizar(reclamo)

    def desadherirse_reclamo(self, id_reclamo: int, id_usu: int) -> None:
        reclamo = self._dao_reclamos.obtener_por_id(id_reclamo)
        if reclamo is None:
            raise ReclamoNoEncontradoError(id_reclamo)
        reclamo.quitar_adherente(id_usu)
        self._dao_reclamos.actualizar(reclamo)

    # Manejar reclamos
    def cambiar_estado_reclamo(self, id_reclamo: int, nuevo_estado: EstadoReclamo,
                                dias_resolucion: int | None = None) -> Reclamo:
        reclamo = self._dao_reclamos.obtener_por_id(id_reclamo)
        if reclamo is None:
            raise ReclamoNoEncontradoError(id_reclamo)
        reclamo.cambiar_estado(nuevo_estado, dias_resolucion)
        return self._dao_reclamos.actualizar(reclamo)

    # secretaría técnica: derivar a otro departamento
    def derivar_reclamo(self, id_reclamo: int, nuevo_departamento_nombre: str) -> Reclamo:
        reclamo = self._dao_reclamos.obtener_por_id(id_reclamo)
        if reclamo is None:
            raise ReclamoNoEncontradoError(id_reclamo)
        nuevo_departamento = self._dao_reclamos.obtener_departamento_por_nombre(nuevo_departamento_nombre)
        if nuevo_departamento is None:
            raise DepartamentoNoEncontradoError(nuevo_departamento_nombre)
        reclamo.departamento = nuevo_departamento
        return self._dao_reclamos.actualizar(reclamo)

    # consultas
    def get_reclamos_completo(self) -> list[Reclamo]:
        return self._dao_reclamos.get_reclamos_completo()

    def obtener_reclamo(self, id_reclamo: int) -> Reclamo:
        reclamo = self._dao_reclamos.obtener_por_id(id_reclamo)
        if reclamo is None:
            raise ReclamoNoEncontradoError(id_reclamo)
        return reclamo

    def get_departamentos(self) -> list[Departamento]:
        return self._dao_reclamos.obtener_todos_los_departamentos()

    def get_reclamo_porautor(self, id: int) -> list[Reclamo]:
        return self._dao_reclamos.get_reclamo_porautor(id)

    def get_reclamos_depto(self, depto: str) -> list[Reclamo]:
        return self._dao_reclamos.get_reclamo_pordepto(depto)

    def get_reclamos_pendientes(self, depto: str | None = None) -> list[Reclamo]:
        reclamos = self.get_reclamos_depto(depto) if depto else self.get_reclamos_completo()
        return [r for r in reclamos if r.estado == EstadoReclamo.PENDIENTE]

    # reportes
    def generar_reporte(self, tipo: str, lista_reclamos: list[Reclamo]) -> Any:
        """
        Orquesta el flujo completo del dashboard de departamento:
        """
        datos = self._analitica.calculardatos(lista_reclamos)
        grafico_tor = self._analitica.generar_grafica_tor(datos)
        grafico_tie = self._analitica.generar_grafica_tie(datos)
        grafico_pa = self._analitica.generar_grafica_pa(datos)
        return self._analitica.generar_reporte(datos, grafico_tor, grafico_tie, grafico_pa, tipo)
