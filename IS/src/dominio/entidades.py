"""Entidades del modelo de dominio (TP1) que intervienen en HU-01.A1: Experimento y ParametroExperimento."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

ESTADOS_VALIDEZ = ("en_curso", "finalizado", "invalido")


def _normalizar(texto: str) -> str:
    return " ".join(texto.split()).casefold()


@dataclass(frozen=True)
class Parametro:
    """ParametroExperimento: un dato nombre-valor-unidad de un experimento (DA-03)."""

    nombre: str
    valor: str
    unidad: Optional[str] = None

    def mismo_valor_que(self, otro_valor: str) -> bool:
        """Compara sin distinguir mayúsculas ni espacios de más."""
        return _normalizar(self.valor) == _normalizar(otro_valor)


@dataclass
class Experimento:
    """Un experimento del catálogo. Conoce sus parámetros y sabe si puede ser coincidencia de otro."""

    proyecto_id: str
    tipo: str
    autor: str
    fecha_hora: datetime
    fecha_realizacion: date
    parametros: list[Parametro] = field(default_factory=list)
    hardware: str = ""
    tiempo_procesamiento: str = ""
    objetivo: str = ""
    hipotesis: str = ""
    notas: str = ""
    estado_validez: str = "en_curso"
    estado_analisis: str = "pendiente"
    similar_a: list[str] = field(default_factory=list)
    id: Optional[str] = None
    ruta_pdb: Optional[str] = None
    rutas_capturas: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.estado_validez not in ESTADOS_VALIDEZ:
            raise ValueError(f"estado de validez desconocido: {self.estado_validez}")

    def valor_de(self, nombre: str) -> Optional[str]:
        for p in self.parametros:
            if p.nombre == nombre:
                return p.valor
        return None

    def coincide_con(self, tipo: str, clave: dict[str, str]) -> bool:
        """Mismo tipo y mismos valores en los parámetros de la clave de coincidencia (RF-03)."""
        if self.tipo != tipo:
            return False
        for nombre, valor in clave.items():
            propio = next((p for p in self.parametros if p.nombre == nombre), None)
            if propio is None or not propio.mismo_valor_que(valor):
                return False
        return True

    def puede_ser_coincidencia(self) -> bool:
        """Un experimento inválido no se reporta como coincidencia (RF-03)."""
        return self.estado_validez != "invalido"

    def declara_similar_a(self, otro_id: str) -> bool:
        return otro_id in self.similar_a
