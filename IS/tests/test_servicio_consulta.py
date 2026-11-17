from src.servicios.servicio_consulta import ServicioConsulta
from tests.conftest import experimento_existente


def test_lista_proyectos_y_experimentos_para_armar_el_formulario(repo):
    repo.guardar(experimento_existente())
    consulta = ServicioConsulta(repo)
    assert consulta.proyectos() == [("P1", "Proyecto uno")]
    assert [e.id for e in consulta.experimentos()] == ["101"]
