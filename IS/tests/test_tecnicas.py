import pytest

from src.dominio.entidades import Parametro
from src.dominio.registro_tecnicas import RegistroTecnicas
from src.dominio.tecnica_docking import TecnicaDocking
from src.transversal.gestion_excepciones import ErrorValidacion


def test_docking_define_proteina_ligando_y_software_como_obligatorios():
    obligatorios = {d.nombre for d in TecnicaDocking().definiciones() if d.obligatorio}
    assert obligatorios == {"proteina", "ligando", "software"}


def test_docking_rechaza_proteina_y_ligando_iguales():
    errores = TecnicaDocking().validar([Parametro("proteina", "Indinavir"), Parametro("ligando", " indinavir ")])
    assert errores and "no pueden ser el mismo" in errores[0]


def test_docking_acepta_proteina_y_ligando_distintos():
    assert TecnicaDocking().validar([Parametro("proteina", "A"), Parametro("ligando", "B")]) == []


def test_docking_clave_de_coincidencia_y_resumen():
    t = TecnicaDocking()
    assert t.clave_coincidencia() == ["proteina", "ligando"] and t.parametros_resumen() == ["proteina", "ligando"]


def test_el_registro_entrega_la_tecnica_registrada():
    registro = RegistroTecnicas()
    docking = TecnicaDocking()
    registro.registrar(docking)
    assert registro.obtener("docking") is docking and registro.disponibles() == [docking]


def test_el_registro_rechaza_un_tipo_desconocido():
    with pytest.raises(ErrorValidacion) as e:
        RegistroTecnicas().obtener("dinamica")
    assert "no está disponible" in e.value.errores[0]
