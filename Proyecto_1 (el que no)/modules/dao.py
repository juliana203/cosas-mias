"""
dao.py

Agrupa el patrón DAO completo: la interfaz abstracta IDao y sus dos
implementaciones concretas con SQLAlchemy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .persistencia import ModeloUsuario, ModeloReclamo, ModeloDepartamento
from .usuarios import Usuario, UsuarioFinal, JefeDepartamento, SecretarioTecnico, Departamento
from .reclamos import Reclamo, EstadoReclamo
from .excepciones import UsuarioNoEncontradoError, ReclamoNoEncontradoError, RolUsuarioDesconocidoError


# IDao
class IDao(ABC):
    @abstractmethod
    def guardar(self, entidad: Any) -> Any:
        ...

    @abstractmethod
    def obtener_por_id(self, id: int) -> Any:
        ...

    @abstractmethod
    def obtener_todos(self) -> list:
        ...

    @abstractmethod
    def actualizar(self, entidad: Any) -> Any:
        ...

    @abstractmethod
    def eliminar(self, id: int) -> None:
        ...

    @abstractmethod
    def obtener_por_filtro(self, filtro: dict) -> Any:
        ...

    @abstractmethod
    def obtener_todos_por_filtro(self, filtro: dict) -> list:
        ...


class DaoUsuarioSQLAlchemy(IDao):
    def __init__(self, session: Session):
        self._session = session

    # mapeo db <-> entidad
    def _map_modelo_a_entidad(self, modelo: ModeloUsuario) -> Usuario:
        if modelo.rol == "usuario_final":
            usuario: Usuario = UsuarioFinal(
                nombre=modelo.nombre, apellido=modelo.apellido, email=modelo.email,
                nombre_usuario=modelo.nombreUsuario, claustro=modelo.claustro,
                contrasena="temporal",  # se sobreescribe abajo con el hash real
                id_bd=modelo.id,
            )
        elif modelo.rol == "jefe_departamento":
            depto = (
                Departamento(nombre=modelo.departamento.nombre, id=modelo.departamento.id)
                if modelo.departamento is not None else None
            )
            usuario = JefeDepartamento(
                nombre=modelo.nombre, apellido=modelo.apellido, email=modelo.email,
                nombre_usuario=modelo.nombreUsuario, contrasena="temporal",
                departamento_asignado=depto, id_bd=modelo.id,
            )
        elif modelo.rol == "secretario_tecnico":
            usuario = SecretarioTecnico(
                nombre=modelo.nombre, apellido=modelo.apellido, email=modelo.email,
                nombre_usuario=modelo.nombreUsuario, contrasena="temporal",
                id_bd=modelo.id,
            )
        else:
            raise RolUsuarioDesconocidoError(modelo.rol)

        Usuario._reconstruir_contrasena(usuario, modelo.contrasena)
        return usuario

    def _map_entidad_a_modelo(self, entidad: Usuario) -> ModeloUsuario:
        modelo = ModeloUsuario(
            id=entidad.id_bd,
            nombre=entidad.nombre,
            apellido=entidad.apellido,
            email=entidad.email,
            nombreUsuario=entidad.nombre_usuario,
            contrasena=entidad.contrasena,
            rol=entidad.rol,
        )
        if isinstance(entidad, UsuarioFinal):
            modelo.claustro = entidad.claustro
        if isinstance(entidad, JefeDepartamento) and entidad.departamento_asignado is not None:
            modelo.departamentoAsignado = entidad.departamento_asignado.id
        return modelo

    # IDao
    def guardar(self, entidad: Usuario) -> Usuario:
        modelo = self._map_entidad_a_modelo(entidad)
        self._session.add(modelo)
        self._session.commit()
        entidad.id_bd = modelo.id
        return entidad

    def obtener_por_id(self, id: int) -> Usuario | None:
        modelo = self._session.get(ModeloUsuario, id)
        return self._map_modelo_a_entidad(modelo) if modelo else None

    def obtener_todos(self) -> list[Usuario]:
        modelos = self._session.execute(select(ModeloUsuario)).scalars().all()
        return [self._map_modelo_a_entidad(m) for m in modelos]

    def actualizar(self, entidad: Usuario) -> Usuario:
        modelo = self._session.get(ModeloUsuario, entidad.id_bd)
        if modelo is None:
            raise UsuarioNoEncontradoError(entidad.id_bd)
        modelo.nombre = entidad.nombre
        modelo.apellido = entidad.apellido
        modelo.email = entidad.email
        modelo.nombreUsuario = entidad.nombre_usuario
        modelo.contrasena = entidad.contrasena
        if isinstance(entidad, UsuarioFinal):
            modelo.claustro = entidad.claustro
        if isinstance(entidad, JefeDepartamento) and entidad.departamento_asignado is not None:
            modelo.departamentoAsignado = entidad.departamento_asignado.id
        self._session.commit()
        return entidad

    def eliminar(self, id: int) -> None:
        modelo = self._session.get(ModeloUsuario, id)
        if modelo is not None:
            self._session.delete(modelo)
            self._session.commit()

    def obtener_por_filtro(self, filtro: dict) -> Usuario | None:
        stmt = select(ModeloUsuario).filter_by(**filtro)
        modelo = self._session.execute(stmt).scalars().first()
        return self._map_modelo_a_entidad(modelo) if modelo else None

    def obtener_todos_por_filtro(self, filtro: dict) -> list[Usuario]:
        stmt = select(ModeloUsuario).filter_by(**filtro)
        modelos = self._session.execute(stmt).scalars().all()
        return [self._map_modelo_a_entidad(m) for m in modelos]

    # Acciones de usuarios (GestorUsuario)
    def inscribiruser(self, datos_usuario: Usuario) -> Usuario:
        """Alta de un nuevo usuario (típicamente un UsuarioFinal recién registrado)."""
        return self.guardar(datos_usuario)

    def filtrarporemail(self, email: str) -> Usuario | None:
        return self.obtener_por_filtro({"email": email})

    def filtrarpornombreusuario(self, nombre_usuario: str) -> Usuario | None:
        return self.obtener_por_filtro({"nombreUsuario": nombre_usuario})

    def obtenerid_usuario(self, user_id: int) -> Usuario | None:
        return self.obtener_por_id(user_id)

    def obtener_usu(self) -> list[Usuario]:
        return self.obtener_todos()


# DaoReclamosSQLAlchemy
class DaoReclamosSQLAlchemy(IDao):
    def __init__(self, session: Session, dao_usuarios: DaoUsuarioSQLAlchemy):
        self._session = session
        self._dao_usuarios = dao_usuarios

    # mapeo db <-> entidad
    def _map_modelo_a_entidad(self, modelo: ModeloReclamo) -> Reclamo:
        creador = self._dao_usuarios.obtener_por_id(modelo.idUsuarioCreador)
        depto = Departamento(nombre=modelo.depto.nombre, id=modelo.depto.id)

        reclamo = Reclamo(
            usuario_creador=creador, contenido=modelo.contenido,
            departamento=depto, id_reclamo=modelo.id,
            ruta_imagen=modelo.rutaImagen,
        )
        reclamo.timestamp = modelo.timestamp

        for adherente_modelo in modelo.adherentes:
            adherente = self._dao_usuarios.obtener_por_id(adherente_modelo.id)
            reclamo.agregar_adherente(adherente)

        estado = EstadoReclamo(modelo.estado)
        if estado == EstadoReclamo.EN_PROCESO:
            # Al reconstruir desde la BD ya contamos con el plazo asignado.
            reclamo.cambiar_estado(estado, modelo.tiempoResolucionAsignado)
        else:
            reclamo.cambiar_estado(estado)
        return reclamo

    def _map_entidad_a_modelo(self, entidad: Reclamo) -> ModeloReclamo:
        return ModeloReclamo(
            id=entidad.id_reclamo,
            contenido=entidad.contenido,
            departamento=entidad.departamento.id,
            timestamp=entidad.timestamp,
            estado=entidad.estado.value,
            tiempoResolucionAsignado=entidad.tiempo_resolucion_asignado,
            idUsuarioCreador=entidad.usuario_creador.id_bd,
            rutaImagen=entidad.ruta_imagen,
        )

    # IDao
    def guardar(self, entidad: Reclamo) -> Reclamo:
        return self.guardar_reclamo(entidad)

    def obtener_por_id(self, id: int) -> Reclamo | None:
        modelo = self._session.get(ModeloReclamo, id)
        return self._map_modelo_a_entidad(modelo) if modelo else None

    def obtener_todos(self) -> list[Reclamo]:
        modelos = self._session.execute(select(ModeloReclamo)).scalars().all()
        return [self._map_modelo_a_entidad(m) for m in modelos]

    def actualizar(self, entidad: Reclamo) -> Reclamo:
        modelo = self._session.get(ModeloReclamo, entidad.id_reclamo)
        if modelo is None:
            raise ReclamoNoEncontradoError(entidad.id_reclamo)
        modelo.contenido = entidad.contenido
        modelo.departamento = entidad.departamento.id
        modelo.estado = entidad.estado.value
        modelo.tiempoResolucionAsignado = entidad.tiempo_resolucion_asignado
        modelo.adherentes = [
            self._session.get(ModeloUsuario, a.id_bd) for a in entidad.adherentes
        ]
        self._session.commit()
        return entidad

    def eliminar(self, id: int) -> None:
        modelo = self._session.get(ModeloReclamo, id)
        if modelo is not None:
            self._session.delete(modelo)
            self._session.commit()

    def obtener_por_filtro(self, filtro: dict) -> Reclamo | None:
        stmt = select(ModeloReclamo).filter_by(**filtro)
        modelo = self._session.execute(stmt).scalars().first()
        return self._map_modelo_a_entidad(modelo) if modelo else None

    def obtener_todos_por_filtro(self, filtro: dict) -> list[Reclamo]:
        stmt = select(ModeloReclamo).filter_by(**filtro)
        modelos = self._session.execute(stmt).scalars().all()
        return [self._map_modelo_a_entidad(m) for m in modelos]

    # Acciones específicas de reclamos
    def guardar_reclamo(self, reclamo: Reclamo) -> Reclamo:
        modelo = self._map_entidad_a_modelo(reclamo)
        self._session.add(modelo)
        self._session.commit()
        reclamo.id_reclamo = modelo.id
        return reclamo

    def adherirse(self, id_reclamo: int, id_usu: int) -> None:
        modelo = self._session.get(ModeloReclamo, id_reclamo)
        if modelo is None:
            raise ReclamoNoEncontradoError(id_reclamo)
        usuario_modelo = self._session.get(ModeloUsuario, id_usu)
        if usuario_modelo is None:
            raise UsuarioNoEncontradoError(id_usu)
        if usuario_modelo not in modelo.adherentes:
            modelo.adherentes.append(usuario_modelo)
            self._session.commit()

    def desadherirse(self, id_reclamo: int, id_usu: int) -> None:
        modelo = self._session.get(ModeloReclamo, id_reclamo)
        if modelo is None:
            raise ReclamoNoEncontradoError(id_reclamo)
        modelo.adherentes = [a for a in modelo.adherentes if a.id != id_usu]
        self._session.commit()

    def get_reclamos_completo(self) -> list[Reclamo]:
        return self.obtener_todos()

    def get_reclamo_porautor(self, id: int) -> list[Reclamo]:
        return self.obtener_todos_por_filtro({"idUsuarioCreador": id})

    def get_reclamo_pordepto(self, depto: str) -> list[Reclamo]:
        stmt = (
            select(ModeloReclamo)
            .join(ModeloDepartamento, ModeloReclamo.departamento == ModeloDepartamento.id)
            .where(ModeloDepartamento.nombre == depto)
        )
        modelos = self._session.execute(stmt).scalars().all()
        return [self._map_modelo_a_entidad(m) for m in modelos]

    def obtener_departamento_por_nombre(self, nombre: str) -> Departamento | None:
        """
        Para resolver a qué Departamento corresponde el nombre devuelto por el clasificador automático,
        y para validar el destino al derivar un reclamo (secretaría técnica).
        """
        stmt = select(ModeloDepartamento).where(ModeloDepartamento.nombre == nombre)
        modelo = self._session.execute(stmt).scalars().first()
        return Departamento(nombre=modelo.nombre, id=modelo.id) if modelo else None

    def obtener_todos_los_departamentos(self) -> list[Departamento]:
        modelos = self._session.execute(select(ModeloDepartamento)).scalars().all()
        return [Departamento(nombre=m.nombre, id=m.id) for m in modelos]

    def crear_departamento(self, nombre: str) -> Departamento:
        existente = self.obtener_departamento_por_nombre(nombre)
        if existente is not None:
            return existente
        modelo = ModeloDepartamento(nombre=nombre)
        self._session.add(modelo)
        self._session.commit()
        return Departamento(nombre=modelo.nombre, id=modelo.id)
