"""
clasificador.py

ClasificadorReclamos — patrón Adapter entre el clasificador
entrenado que provee la cátedra y lo que necesita GestorReclamos 
(el protocolo `IClasificadorReclamos` de gestores.py:
`clasificar(contenido: str) -> str`).
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

from .excepciones import ContenidoVacioError

DEPARTAMENTOS_CLASIFICADOR: tuple[str, ...] = (
    "soporte informático",
    "secretaría técnica",
    "maestranza",
)

class ClasificadorReclamos:
    def __init__(self, clf: Any):
        self._clf = clf

    @classmethod
    def desde_pickle(cls, ruta_pickle: str | Path) -> "ClasificadorReclamos":
        
        with open(ruta_pickle, "rb") as archivo:
            clf = pickle.load(archivo)
        return cls(clf)

    def clasificar(self, p_reclamo: str) -> str:
        if not p_reclamo or not p_reclamo.strip():
            raise ContenidoVacioError()
        resultado = self._clf.classify([p_reclamo])
        return resultado[0]
