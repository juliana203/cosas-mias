from __future__ import annotations

from abc import ABC, abstractmethod

from ..solicitud import SolicitudRegistro


class Paso(ABC):
    """Un paso del núcleo de registro. Los pasos no se llaman entre sí: los ejecuta el Ejecutor de registro."""

    @abstractmethod
    def ejecutar(self, solicitud: SolicitudRegistro) -> None: ...
