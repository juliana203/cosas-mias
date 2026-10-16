"""
reclamos.py

Agrupa EstadoReclamo (enum) y Reclamo, la entidad central del dominio.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from .usuarios import UsuarioFinal, Departamento
from .excepciones import AutoAdhesionError, AdhesionDuplicadaError, TransicionEstadoInvalidaError


# EstadoReclamo

class EstadoReclamo(Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"
    INVALIDO = "invalido"

    def __str__(self) -> str:
        return self.value


# Reclamo

class Reclamo:
    def __init__(self, usuario_creador: UsuarioFinal, contenido: str,
                 departamento: Departamento, id_reclamo: int | None = None,
                 ruta_imagen: str | None = None):
        self._id_reclamo = id_reclamo
        self._usuario_creador = usuario_creador
        self._contenido = contenido
        self._departamento = departamento
        self._timestamp: datetime = datetime.now()
        self._estado: EstadoReclamo = EstadoReclamo.PENDIENTE
        self._adherentes: list[UsuarioFinal] = []
        self._tiempo_resolucion_asignado: int | None = None
        self._ruta_imagen: str | None = ruta_imagen


    @property
    def id_reclamo(self) -> int | None:
        return self._id_reclamo

    @id_reclamo.setter
    def id_reclamo(self, value: int) -> None:
        self._id_reclamo = value

    @property
    def usuario_creador(self) -> UsuarioFinal:
        return self._usuario_creador

    @property
    def contenido(self) -> str:
        return self._contenido

    @property
    def departamento(self) -> Departamento:
        return self._departamento

    @departamento.setter
    def departamento(self, nuevo_departamento: Departamento) -> None:
        # Habilita la derivación de un reclamo a otro departamento
        self._departamento = nuevo_departamento

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: datetime) -> None:
        # Para restaurar la fecha/hora original al reconstruir desde la BD (lo usa persistencia)
        self._timestamp = value

    @property
    def estado(self) -> EstadoReclamo:
        return self._estado

    @property
    def adherentes(self) -> list[UsuarioFinal]:
        return list(self._adherentes)  # copia defensiva

    @property
    def tiempo_resolucion_asignado(self) -> int | None:
        return self._tiempo_resolucion_asignado

    @property
    def ruta_imagen(self) -> str | None:
        """
        Ruta relativa a static/ de la foto adjunta para usar con url_for('static', filename=...) 
        en los templates.
        None si el reclamo no tiene foto.
        """
        return self._ruta_imagen

    # Comportamiento
    def agregar_adherente(self, usuario: UsuarioFinal) -> None:
        if self._usuario_creador.id_bd is not None and usuario.id_bd == self._usuario_creador.id_bd:
            raise AutoAdhesionError()
        if any(a.id_bd == usuario.id_bd for a in self._adherentes):
            raise AdhesionDuplicadaError()
        self._adherentes.append(usuario)

    def quitar_adherente(self, id_usuario: int) -> None:
        self._adherentes = [a for a in self._adherentes if a.id_bd != id_usuario]

    def cambiar_estado(self, nuevo_estado: EstadoReclamo, dias_resolucion: int | None = None) -> None:
        if nuevo_estado == EstadoReclamo.EN_PROCESO:
            if dias_resolucion is None or not (1 <= dias_resolucion <= 15):
                raise TransicionEstadoInvalidaError(dias_resolucion)
            self._tiempo_resolucion_asignado = dias_resolucion
        self._estado = nuevo_estado

    def __repr__(self) -> str:
        return (f"Reclamo(id={self._id_reclamo}, estado={self._estado.value}, "
                f"departamento='{self._departamento.nombre}', "
                f"adherentes={len(self._adherentes)})")
