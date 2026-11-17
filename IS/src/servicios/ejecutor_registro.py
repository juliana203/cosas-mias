"""Capa de servicios: intermediaria, sin reglas de negocio ni de ninguna técnica."""
from __future__ import annotations

from ..dominio.entidades import Experimento
from ..dominio.pasos.paso import Paso
from ..dominio.registro_tecnicas import RegistroTecnicas
from ..dominio.solicitud import DatosRegistro, SolicitudRegistro


class EjecutorRegistro:
    """Crea la solicitud de registro, pide la técnica y ejecuta los pasos en orden."""

    def __init__(self, registro_tecnicas: RegistroTecnicas, pasos: list[Paso]):
        self._tecnicas = registro_tecnicas
        self._pasos = pasos

    def registrar(self, datos: DatosRegistro, autor: str, confirmado: bool = False) -> Experimento:
        tecnica = self._tecnicas.obtener(datos.tipo)
        solicitud = SolicitudRegistro(datos=datos, autor=autor, tecnica=tecnica, confirmada=confirmado)
        for paso in self._pasos:
            paso.ejecutar(solicitud)
        return solicitud.experimento
