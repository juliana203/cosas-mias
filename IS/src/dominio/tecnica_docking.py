from __future__ import annotations

from .entidades import Parametro
from .tecnica import DefinicionParametro, Tecnica


class TecnicaDocking(Tecnica):
    """Plug-in de docking molecular: la única técnica que se construye en este TP."""

    tipo = "docking"
    etiqueta = "Docking molecular"

    def definiciones(self) -> list[DefinicionParametro]:
        return [
            DefinicionParametro("proteina", "Molécula / Proteína", obligatorio=True),
            DefinicionParametro("ligando", "Ligando", obligatorio=True),
            DefinicionParametro("software", "Software utilizado", obligatorio=True, max_largo=60),
        ]

    def validar(self, parametros: list[Parametro]) -> list[str]:
        valores = {p.nombre: p.valor for p in parametros}
        proteina, ligando = valores.get("proteina"), valores.get("ligando")
        if proteina and ligando and proteina.strip().casefold() == ligando.strip().casefold():
            return ["La molécula/proteína y el ligando no pueden ser el mismo."]
        return []

    def clave_coincidencia(self) -> list[str]:
        return ["proteina", "ligando"]

    def parametros_resumen(self) -> list[str]:
        return ["proteina", "ligando"]
