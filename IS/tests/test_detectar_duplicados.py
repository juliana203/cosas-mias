import pytest

from src.dominio.pasos.detectar_duplicados import DetectarDuplicados
from src.dominio.solicitud import SolicitudRegistro
from src.dominio.tecnica_docking import TecnicaDocking
from src.transversal.gestion_excepciones import PideConfirmacion
from tests.conftest import datos_validos, experimento_existente


@pytest.fixture
def paso(repo):
    return DetectarDuplicados(repo)


def solicitud(confirmada=False, **cambios):
    return SolicitudRegistro(datos=datos_validos(**cambios), autor="ana", tecnica=TecnicaDocking(), confirmada=confirmada)


def test_sin_coincidencias_el_registro_sigue(paso):
    s = solicitud()
    paso.ejecutar(s)
    assert s.coincidencias == []


def test_con_coincidencia_sin_confirmar_corta_y_devuelve_la_lista(paso, repo):
    repo.guardar(experimento_existente())
    with pytest.raises(PideConfirmacion) as e:
        paso.ejecutar(solicitud())
    assert len(e.value.coincidencias) == 1


def test_con_coincidencia_confirmada_el_registro_sigue(paso, repo):
    repo.guardar(experimento_existente())
    s = solicitud(confirmada=True)
    paso.ejecutar(s)
    assert len(s.coincidencias) == 1


def test_un_experimento_invalido_no_es_coincidencia(paso, repo):
    repo.guardar(experimento_existente(estado="invalido"))
    s = solicitud()
    paso.ejecutar(s)
    assert s.coincidencias == []


def test_un_experimento_declarado_en_similar_a_no_se_reporta(paso, repo):
    otro_id = repo.guardar(experimento_existente())
    s = solicitud(similar_a=[otro_id])
    paso.ejecutar(s)
    assert s.coincidencias == []


def test_otro_ligando_no_es_coincidencia(paso, repo):
    repo.guardar(experimento_existente(ligando="Ritonavir"))
    paso.ejecutar(solicitud())


def test_otro_tipo_de_experimento_no_es_coincidencia(paso, repo):
    repo.guardar(experimento_existente(tipo="dinamica"))
    paso.ejecutar(solicitud())


def test_detectar_no_escribe_nada(paso, repo):
    repo.guardar(experimento_existente())
    antes = len(repo.todos())
    with pytest.raises(PideConfirmacion):
        paso.ejecutar(solicitud())
    assert len(repo.todos()) == antes
