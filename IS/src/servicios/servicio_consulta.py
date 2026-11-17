"""Apoyo de la interfaz: lista proyectos y experimentos para armar el formulario (no es parte de HU-01.A1)."""
from __future__ import annotations

from ..acceso_datos.repositorio_en_memoria import RepositorioExperimentosEnMemoria


class ServicioConsulta:
    def __init__(self, repositorio: RepositorioExperimentosEnMemoria):
        self._repo = repositorio

    def proyectos(self) -> list[tuple[str, str]]:
        return self._repo.proyectos()

    def experimentos(self):
        return self._repo.todos()
