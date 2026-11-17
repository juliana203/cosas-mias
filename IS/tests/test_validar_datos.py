from datetime import date

import pytest

from src.dominio.entidades import Parametro
from src.dominio.pasos.validar_datos import ValidarDatos
from src.dominio.solicitud import SolicitudRegistro
from src.dominio.tecnica_docking import TecnicaDocking
from src.transversal.gestion_excepciones import ErrorValidacion
from tests.conftest import HOY, datos_validos, experimento_existente


@pytest.fixture
def paso(repo):
    return ValidarDatos(repo, hoy=lambda: HOY)


def solicitud(**cambios):
    return SolicitudRegistro(datos=datos_validos(**cambios), autor="ana", tecnica=TecnicaDocking())


def errores_de(paso, **cambios):
    with pytest.raises(ErrorValidacion) as e:
        paso.ejecutar(solicitud(**cambios))
    return e.value.errores


def test_datos_validos_pasan(paso):
    paso.ejecutar(solicitud())


def test_proyecto_inexistente(paso):
    assert any("proyecto" in m for m in errores_de(paso, proyecto_id="PX"))


def test_fecha_vacia(paso):
    assert any("fecha" in m.lower() for m in errores_de(paso, fecha_realizacion=None))


def test_fecha_futura_se_rechaza_pero_hoy_se_acepta(paso):
    assert any("futura" in m for m in errores_de(paso, fecha_realizacion=date(2026, 11, 11)))
    paso.ejecutar(solicitud(fecha_realizacion=HOY))


def test_pdb_obligatorio(paso):
    assert any("PDB" in m for m in errores_de(paso, pdb=None))


@pytest.mark.parametrize("campo", ["proteina", "ligando", "software"])
def test_parametro_obligatorio_de_la_tecnica_vacio(paso, campo):
    valores = {"proteina": "A", "ligando": "B", "software": "Vina", campo: "   "}
    assert errores_de(paso, valores=valores)


def test_largo_maximo_en_el_limite_pasa_y_uno_mas_falla(paso):
    paso.ejecutar(solicitud(valores={"proteina": "A" * 100, "ligando": "B", "software": "V"}))
    assert errores_de(paso, valores={"proteina": "A" * 101, "ligando": "B", "software": "V"})


def test_parametro_extra_sin_nombre(paso):
    assert any("no tiene nombre" in m for m in errores_de(paso, extras=[Parametro("", "5")]))


def test_similar_a_inexistente(paso):
    assert any("Similar a" in m for m in errores_de(paso, similar_a=["999"]))


def test_similar_a_existente_pasa(paso, repo):
    otro_id = repo.guardar(experimento_existente())
    paso.ejecutar(solicitud(similar_a=[otro_id]))


def test_regla_propia_de_la_tecnica_proteina_igual_a_ligando(paso):
    assert any("mismo" in m for m in errores_de(paso, valores={"proteina": "X", "ligando": "x", "software": "V"}))


def test_informa_todos_los_errores_juntos(paso):
    errores = errores_de(paso, proyecto_id="PX", pdb=None, valores={"proteina": "", "ligando": "", "software": ""})
    assert len(errores) >= 5
