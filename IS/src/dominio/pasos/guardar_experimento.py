from __future__ import annotations

from datetime import datetime
from typing import Callable

from ...transversal.gestion_excepciones import ErrorAlmacenamiento
from ..entidades import Experimento
from ..puertos import AccesoArchivos, RepositorioExperimentos
from ..solicitud import SolicitudRegistro
from .paso import Paso


class GuardarExperimento(Paso):
    """Paso 3: registra autor y fecha, guarda el experimento y después sus archivos; revierte si algo falla.

    Siempre crea un experimento nuevo: nunca sobrescribe ni vincula uno existente (HU-01.A1).
    """

    def __init__(
        self,
        repositorio: RepositorioExperimentos,
        archivos: AccesoArchivos,
        ahora: Callable[[], datetime] = datetime.now,
    ):
        self._repo = repositorio
        self._archivos = archivos
        self._ahora = ahora

    def ejecutar(self, solicitud: SolicitudRegistro) -> None:
        d = solicitud.datos
        experimento = Experimento(
            proyecto_id=d.proyecto_id,
            tipo=d.tipo,
            autor=solicitud.autor,
            fecha_hora=self._ahora(),
            fecha_realizacion=d.fecha_realizacion,
            parametros=solicitud.parametros(),
            hardware=d.hardware.strip(),
            tiempo_procesamiento=d.tiempo_procesamiento.strip(),
            objetivo=d.objetivo.strip(),
            hipotesis=d.hipotesis.strip(),
            notas=d.notas.strip(),
            estado_validez=d.estado_validez,
            similar_a=list(d.similar_a),
        )
        experimento.id = self._repo.guardar(experimento)
        try:
            experimento.ruta_pdb = self._archivos.guardar_pdb(experimento.id, d.pdb)
            experimento.rutas_capturas = [
                self._archivos.guardar_captura(experimento.id, nombre, contenido) for nombre, contenido in d.capturas
            ]
            self._repo.actualizar_rutas(experimento)
        except Exception as causa:
            self._repo.eliminar(experimento.id)
            self._archivos.eliminar_archivos(experimento.id)
            raise ErrorAlmacenamiento(str(causa)) from causa
        solicitud.experimento = experimento
