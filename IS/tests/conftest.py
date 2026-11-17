from datetime import date, datetime

import pytest

from src.acceso_datos.archivos_en_memoria import AccesoArchivosEnMemoria
from src.acceso_datos.repositorio_en_memoria import RepositorioExperimentosEnMemoria
from src.arranque import construir_nucleo
from src.dominio.entidades import Experimento, Parametro
from src.dominio.solicitud import DatosRegistro

HOY = date(2026, 11, 10)
AHORA = datetime(2026, 11, 10, 9, 30)


def datos_validos(**cambios) -> DatosRegistro:
    base = dict(
        proyecto_id="P1",
        tipo="docking",
        fecha_realizacion=date(2026, 11, 1),
        valores={"proteina": "Proteasa HIV-1", "ligando": "Indinavir", "software": "AutoDock Vina"},
        pdb=b"ATOM      1  N   ALA A   1\nEND\n",
    )
    base.update(cambios)
    return DatosRegistro(**base)


def experimento_existente(proteina="Proteasa HIV-1", ligando="Indinavir", estado="finalizado", tipo="docking") -> Experimento:
    return Experimento(
        proyecto_id="P1",
        tipo=tipo,
        autor="otra.persona",
        fecha_hora=datetime(2026, 10, 1, 8, 0),
        fecha_realizacion=date(2026, 10, 1),
        parametros=[Parametro("proteina", proteina), Parametro("ligando", ligando)],
        estado_validez=estado,
    )


@pytest.fixture
def repo():
    return RepositorioExperimentosEnMemoria({"P1": "Proyecto uno"})


@pytest.fixture
def archivos():
    return AccesoArchivosEnMemoria()


@pytest.fixture
def sistema(repo, archivos):
    """Núcleo real con persistencia y archivos en memoria."""
    registro, ejecutor = construir_nucleo(repo, archivos)
    return registro, ejecutor
