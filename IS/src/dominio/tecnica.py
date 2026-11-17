"""Interfaz de técnica: lo propio de cada ensayo (TP3 5.2.2, DA-02)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .entidades import Parametro


@dataclass(frozen=True)
class DefinicionParametro:
    nombre: str
    etiqueta: str
    unidad: Optional[str] = None
    obligatorio: bool = False
    max_largo: int = 100


class Tecnica(ABC):
    tipo: str
    etiqueta: str

    @abstractmethod
    def definiciones(self) -> list[DefinicionParametro]:
        """Parámetros de la técnica: nombre, unidad, obligatoriedad y formato."""

    @abstractmethod
    def validar(self, parametros: list[Parametro]) -> list[str]:
        """Validaciones propias entre parámetros. Devuelve los errores encontrados."""

    @abstractmethod
    def clave_coincidencia(self) -> list[str]:
        """Nombres de los parámetros que definen que dos experimentos son el mismo (RF-03)."""

    @abstractmethod
    def parametros_resumen(self) -> list[str]:
        """Parámetros que se muestran en el listado."""
