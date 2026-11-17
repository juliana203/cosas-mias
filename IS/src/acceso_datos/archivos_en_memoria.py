from __future__ import annotations

from ..dominio.puertos import AccesoArchivos


class AccesoArchivosEnMemoria(AccesoArchivos):
    """Almacén simulado: guarda los bytes en un diccionario indexado por ruta (en producción: servidor de archivos)."""

    def __init__(self) -> None:
        self.archivos: dict[str, bytes] = {}

    def guardar_pdb(self, experimento_id: str, contenido: bytes) -> str:
        ruta = f"pdb/{experimento_id}.pdb"
        self.archivos[ruta] = contenido
        return ruta

    def guardar_captura(self, experimento_id: str, nombre: str, contenido: bytes) -> str:
        ruta = f"capturas/{experimento_id}/{nombre}"
        self.archivos[ruta] = contenido
        return ruta

    def eliminar_archivos(self, experimento_id: str) -> None:
        for ruta in [r for r in self.archivos if r in (f"pdb/{experimento_id}.pdb",) or r.startswith(f"capturas/{experimento_id}/")]:
            del self.archivos[ruta]
