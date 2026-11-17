import pytest

from src.acceso_datos.archivos_en_memoria import AccesoArchivosEnMemoria
from src.dominio.pasos.guardar_experimento import GuardarExperimento
from src.dominio.solicitud import SolicitudRegistro
from src.dominio.tecnica_docking import TecnicaDocking
from src.transversal.gestion_excepciones import ErrorAlmacenamiento
from tests.conftest import AHORA, datos_validos


class ArchivosQueFallan(AccesoArchivosEnMemoria):
    """Doble de prueba: guarda el PDB y falla al guardar la captura (se interrumpe el guardado, CU-01 E2)."""

    def guardar_captura(self, experimento_id, nombre, contenido):
        raise OSError("disco desconectado")


def solicitud(**cambios):
    return SolicitudRegistro(datos=datos_validos(**cambios), autor="ana", tecnica=TecnicaDocking())


def test_guarda_con_autor_fecha_parametros_y_archivo(repo, archivos):
    s = solicitud()
    GuardarExperimento(repo, archivos, ahora=lambda: AHORA).ejecutar(s)
    e = s.experimento
    assert (e.autor, e.fecha_hora, e.id) == ("ana", AHORA, "101")
    assert [(p.nombre, p.valor) for p in e.parametros] == [
        ("proteina", "Proteasa HIV-1"), ("ligando", "Indinavir"), ("software", "AutoDock Vina")]
    assert e.ruta_pdb == "pdb/101.pdb" and archivos.archivos["pdb/101.pdb"].startswith(b"ATOM")
    assert repo.existe_experimento("101")


def test_los_campos_opcionales_vacios_no_impiden_guardar(repo, archivos):
    s = solicitud()
    GuardarExperimento(repo, archivos, ahora=lambda: AHORA).ejecutar(s)
    e = s.experimento
    assert (e.hardware, e.objetivo, e.hipotesis, e.notas, e.rutas_capturas) == ("", "", "", "", [])


def test_guarda_las_capturas_en_el_almacen(repo, archivos):
    s = solicitud(capturas=[("pose.png", b"png")])
    GuardarExperimento(repo, archivos).ejecutar(s)
    assert s.experimento.rutas_capturas == ["capturas/101/pose.png"]


def test_dos_registros_iguales_crean_dos_experimentos_distintos(repo, archivos):
    paso = GuardarExperimento(repo, archivos)
    s1, s2 = solicitud(), solicitud()
    paso.ejecutar(s1)
    paso.ejecutar(s2)
    assert s1.experimento.id != s2.experimento.id and len(repo.todos()) == 2


def test_si_falla_el_guardado_de_archivos_se_revierte_todo(repo):
    archivos = ArchivosQueFallan()
    s = solicitud(capturas=[("pose.png", b"png")])
    with pytest.raises(ErrorAlmacenamiento):
        GuardarExperimento(repo, archivos).ejecutar(s)
    assert repo.todos() == [] and archivos.archivos == {} and s.experimento is None
