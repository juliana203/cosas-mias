"""Solicitud de registro: el único objeto que viaja por los pasos del registro (TP3 5.2.2)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from .entidades import Experimento, Parametro


@dataclass
class DatosRegistro:
    """Lo que el usuario completó en el formulario."""

    proyecto_id: str
    tipo: str
    fecha_realizacion: Optional[date]
    valores: dict[str, str] = field(default_factory=dict)  # parámetros que define la técnica
    extras: list[Parametro] = field(default_factory=list)  # parámetros adicionales libres
    hardware: str = ""
    tiempo_procesamiento: str = ""
    objetivo: str = ""
    hipotesis: str = ""
    notas: str = ""
    similar_a: list[str] = field(default_factory=list)
    estado_validez: str = "en_curso"
    pdb: Optional[bytes] = None
    capturas: list[tuple[str, bytes]] = field(default_factory=list)


@dataclass
class SolicitudRegistro:
    datos: DatosRegistro
    autor: str
    tecnica: "object"  # Tecnica elegida por el Ejecutor de registro
    confirmada: bool = False
    coincidencias: list[Experimento] = field(default_factory=list)
    experimento: Optional[Experimento] = None

    def parametros(self) -> list[Parametro]:
        """Parámetros del experimento: los que define la técnica (con su unidad) y los extras."""
        lista: list[Parametro] = []
        for d in self.tecnica.definiciones():
            valor = self.datos.valores.get(d.nombre, "").strip()
            if valor:
                lista.append(Parametro(d.nombre, valor, d.unidad))
        lista.extend(self.datos.extras)
        return lista

    def clave_de_coincidencia(self) -> dict[str, str]:
        return {n: self.datos.valores.get(n, "").strip() for n in self.tecnica.clave_coincidencia()}
