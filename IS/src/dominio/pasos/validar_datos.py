from __future__ import annotations

from datetime import date
from typing import Callable

from ...transversal.gestion_excepciones import ErrorValidacion
from ..puertos import RepositorioExperimentos
from ..solicitud import SolicitudRegistro
from .paso import Paso


class ValidarDatos(Paso):
    """Paso 1: obligatoriedad y formato, con lo que define la técnica del experimento (RF-08)."""

    def __init__(self, repositorio: RepositorioExperimentos, hoy: Callable[[], date] = date.today):
        self._repo = repositorio
        self._hoy = hoy

    def ejecutar(self, solicitud: SolicitudRegistro) -> None:
        d = solicitud.datos
        errores: list[str] = []
        if not self._repo.existe_proyecto(d.proyecto_id):
            errores.append("El proyecto elegido no existe.")
        if d.fecha_realizacion is None:
            errores.append("La fecha de realización es obligatoria.")
        elif d.fecha_realizacion > self._hoy():
            errores.append("La fecha de realización no puede ser futura.")
        if not d.pdb:
            errores.append("El archivo PDB es obligatorio.")
        for definicion in solicitud.tecnica.definiciones():
            valor = d.valores.get(definicion.nombre, "").strip()
            if definicion.obligatorio and not valor:
                errores.append(f"{definicion.etiqueta} es obligatorio.")
            elif len(valor) > definicion.max_largo:
                errores.append(f"{definicion.etiqueta} supera los {definicion.max_largo} caracteres.")
        for extra in d.extras:
            if not extra.nombre.strip():
                errores.append("Un parámetro adicional tiene valor pero no tiene nombre.")
        for otro_id in d.similar_a:
            if not self._repo.existe_experimento(otro_id):
                errores.append(f"El experimento '{otro_id}' indicado en 'Similar a' no existe.")
        if not errores:
            errores.extend(solicitud.tecnica.validar(solicitud.parametros()))
        if errores:
            raise ErrorValidacion(errores)
