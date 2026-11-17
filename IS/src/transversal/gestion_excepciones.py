"""Gestión de excepciones (aspecto transversal, TP3 sección 5.4).

Define los errores previstos del registro y los traduce en respuestas para el usuario.
"""
from __future__ import annotations


class ErrorPrevisto(Exception):
    """Error que el sistema espera y sabe explicar al usuario."""


class ErrorValidacion(ErrorPrevisto):
    """Faltan datos o tienen un formato inválido (CU-01 E5 y E6)."""

    def __init__(self, errores: list[str]):
        super().__init__("; ".join(errores))
        self.errores = list(errores)


class PideConfirmacion(ErrorPrevisto):
    """Hay coincidencias sin confirmar: el registro se corta y el usuario decide (CU-01, HU-01.A1 y E3)."""

    def __init__(self, coincidencias: list):
        super().__init__(f"{len(coincidencias)} posible(s) coincidencia(s) sin confirmar")
        self.coincidencias = list(coincidencias)


class ErrorAlmacenamiento(ErrorPrevisto):
    """Falló el guardado de archivos; lo guardado se revirtió (CU-01 E2)."""

    def __init__(self, detalle: str):
        super().__init__(detalle)
        self.detalle = detalle


def traducir(error: ErrorPrevisto) -> dict:
    """Convierte un error previsto en la respuesta que arma la pantalla: tipo y mensajes."""
    if isinstance(error, ErrorValidacion):
        return {"tipo": "validacion", "mensajes": error.errores}
    if isinstance(error, PideConfirmacion):
        return {"tipo": "coincidencias", "mensajes": [str(error)]}
    if isinstance(error, ErrorAlmacenamiento):
        return {
            "tipo": "almacenamiento",
            "mensajes": ["No se pudo guardar el archivo; el registro se canceló y no quedó nada guardado."],
        }
    return {"tipo": "desconocido", "mensajes": [str(error)]}
