import pytest

from src.dominio.entidades import Experimento, Parametro
from tests.conftest import experimento_existente


def test_parametro_compara_sin_distinguir_mayusculas_ni_espacios_de_mas():
    assert Parametro("proteina", "Proteasa HIV-1").mismo_valor_que("  proteasa   hiv-1 ")


def test_parametro_con_otro_valor_no_coincide():
    assert not Parametro("ligando", "Indinavir").mismo_valor_que("Ritonavir")


def test_experimento_coincide_con_mismo_tipo_y_misma_clave():
    e = experimento_existente()
    assert e.coincide_con("docking", {"proteina": "proteasa hiv-1", "ligando": "INDINAVIR"})


def test_experimento_de_otro_tipo_no_coincide():
    assert not experimento_existente().coincide_con("dinamica", {"proteina": "Proteasa HIV-1"})


def test_experimento_con_otro_ligando_no_coincide():
    assert not experimento_existente().coincide_con("docking", {"proteina": "Proteasa HIV-1", "ligando": "Ritonavir"})


def test_experimento_sin_el_parametro_de_la_clave_no_coincide():
    assert not experimento_existente().coincide_con("docking", {"software": "Vina"})


@pytest.mark.parametrize("estado,esperado", [("en_curso", True), ("finalizado", True), ("invalido", False)])
def test_solo_los_invalidos_no_pueden_ser_coincidencia(estado, esperado):
    assert experimento_existente(estado=estado).puede_ser_coincidencia() is esperado


def test_estado_de_validez_desconocido_se_rechaza():
    with pytest.raises(ValueError):
        experimento_existente(estado="raro")


def test_valor_de_devuelve_none_si_no_hay_parametro():
    assert experimento_existente().valor_de("software") is None


def test_declara_similar_a():
    e = experimento_existente()
    e.similar_a = ["101"]
    assert e.declara_similar_a("101") and not e.declara_similar_a("102")
