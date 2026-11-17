from __future__ import annotations

from ...transversal.gestion_excepciones import PideConfirmacion
from ..puertos import RepositorioExperimentos
from ..solicitud import SolicitudRegistro
from .paso import Paso


class DetectarDuplicados(Paso):
    """Paso 2: busca coincidencias y corta el registro si no fueron confirmadas (RF-03, RF-04, CU-00).

    No escribe nada. Si el usuario ya confirmó, deja seguir sin vincular el experimento existente.
    """

    def __init__(self, repositorio: RepositorioExperimentos):
        self._repo = repositorio

    def ejecutar(self, solicitud: SolicitudRegistro) -> None:
        candidatas = self._repo.buscar_coincidencias(solicitud.datos.tipo, solicitud.clave_de_coincidencia())
        solicitud.coincidencias = [
            e
            for e in candidatas
            if e.puede_ser_coincidencia() and e.id not in solicitud.datos.similar_a
        ]
        if solicitud.coincidencias and not solicitud.confirmada:
            raise PideConfirmacion(solicitud.coincidencias)
