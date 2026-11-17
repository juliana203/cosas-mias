"""Puertos hacia la capa de acceso a datos: el dominio los define y el acceso a datos los implementa."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .entidades import Experimento


class RepositorioExperimentos(ABC):
    @abstractmethod
    def existe_proyecto(self, proyecto_id: str) -> bool: ...

    @abstractmethod
    def existe_experimento(self, experimento_id: str) -> bool: ...

    @abstractmethod
    def buscar_coincidencias(self, tipo: str, clave: dict[str, str]) -> list[Experimento]:
        """Experimentos del mismo tipo con los mismos valores de la clave (sin excluir ninguno)."""

    @abstractmethod
    def guardar(self, experimento: Experimento) -> str:
        """Guarda el experimento, le asigna un id y lo devuelve."""

    @abstractmethod
    def actualizar_rutas(self, experimento: Experimento) -> None: ...

    @abstractmethod
    def eliminar(self, experimento_id: str) -> None: ...


class AccesoArchivos(ABC):
    @abstractmethod
    def guardar_pdb(self, experimento_id: str, contenido: bytes) -> str:
        """Guarda el PDB y devuelve su ruta (por ejemplo, pdb/101.pdb)."""

    @abstractmethod
    def guardar_captura(self, experimento_id: str, nombre: str, contenido: bytes) -> str: ...

    @abstractmethod
    def eliminar_archivos(self, experimento_id: str) -> None: ...
