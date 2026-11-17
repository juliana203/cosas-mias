"""Pruebas de HU-01.A1 (con B1.1 como base) y del escenario EC-07 a través del Ejecutor de registro."""
from datetime import date

import pytest

from src.arranque import construir_nucleo
from src.dominio.entidades import Parametro
from src.dominio.pasos.paso import Paso
from src.dominio.registro_tecnicas import RegistroTecnicas
from src.dominio.tecnica import DefinicionParametro, Tecnica
from src.dominio.tecnica_docking import TecnicaDocking
from src.servicios.ejecutor_registro import EjecutorRegistro
from src.transversal.gestion_excepciones import ErrorValidacion, PideConfirmacion
from tests.conftest import datos_validos, experimento_existente


def test_cp01_sin_coincidencias_registra_con_autor_y_fecha(sistema, repo, archivos):
    _, ejecutor = sistema
    e = ejecutor.registrar(datos_validos(), autor="ana")
    assert e.autor == "ana" and e.fecha_hora is not None and repo.existe_experimento(e.id)
    assert e.ruta_pdb in archivos.archivos


def test_cp02_un_experimento_previo_invalido_no_se_reporta_y_se_guarda_normal(sistema, repo):
    _, ejecutor = sistema
    repo.guardar(experimento_existente(estado="invalido"))
    e = ejecutor.registrar(datos_validos(), autor="ana")
    assert e.id is not None and len(repo.todos()) == 2


def test_cp03_con_opcionales_vacios_se_guarda_sin_exigirlos(sistema):
    _, ejecutor = sistema
    e = ejecutor.registrar(datos_validos(hardware="", tiempo_procesamiento="", objetivo="", hipotesis="", notas=""), "ana")
    assert e.hardware == "" and e.notas == ""


def test_cp04_con_coincidencia_el_registro_se_corta_y_no_se_guarda_nada(sistema, repo, archivos):
    _, ejecutor = sistema
    existente_id = repo.guardar(experimento_existente())
    with pytest.raises(PideConfirmacion) as e:
        ejecutor.registrar(datos_validos(), autor="ana")
    assert [c.id for c in e.value.coincidencias] == [existente_id]
    assert len(repo.todos()) == 1 and archivos.archivos == {}


def test_cp05_continuar_registra_un_experimento_nuevo_sin_tocar_el_existente(sistema, repo):
    _, ejecutor = sistema
    existente_id = repo.guardar(experimento_existente())
    antes = repo.todos()[0]
    nuevo = ejecutor.registrar(datos_validos(), autor="ana", confirmado=True)
    assert nuevo.id != existente_id and len(repo.todos()) == 2
    assert nuevo.similar_a == [] and repo.todos()[0] == antes


def test_cp06_el_registro_confirmado_usa_los_mismos_datos_sin_recargarlos(sistema, repo):
    _, ejecutor = sistema
    repo.guardar(experimento_existente())
    datos = datos_validos()
    with pytest.raises(PideConfirmacion):
        ejecutor.registrar(datos, autor="ana")
    nuevo = ejecutor.registrar(datos, autor="ana", confirmado=True)  # mismo objeto, nada para recargar
    assert nuevo.valor_de("ligando") == "Indinavir"


def test_cp07_con_varias_coincidencias_las_informa_todas(sistema, repo):
    _, ejecutor = sistema
    repo.guardar(experimento_existente())
    repo.guardar(experimento_existente(estado="en_curso"))
    with pytest.raises(PideConfirmacion) as e:
        ejecutor.registrar(datos_validos(), autor="ana")
    assert len(e.value.coincidencias) == 2


def test_cp08_datos_invalidos_se_rechazan_antes_de_buscar_duplicados(sistema, repo):
    _, ejecutor = sistema
    repo.guardar(experimento_existente())
    with pytest.raises(ErrorValidacion):  # y no PideConfirmacion: validar es el paso 1
        ejecutor.registrar(datos_validos(pdb=None), autor="ana")
    assert len(repo.todos()) == 1


def test_cp09_tipo_desconocido(sistema):
    _, ejecutor = sistema
    with pytest.raises(ErrorValidacion):
        ejecutor.registrar(datos_validos(tipo="cristalografia"), autor="ana")


def test_cp10_el_ejecutor_corre_los_pasos_en_orden_y_se_detiene_si_uno_falla():
    llamadas = []

    class Espia(Paso):
        def __init__(self, nombre, falla=False):
            self.nombre, self.falla = nombre, falla

        def ejecutar(self, solicitud):
            llamadas.append(self.nombre)
            if self.falla:
                raise ErrorValidacion(["x"])

    registro = RegistroTecnicas()
    registro.registrar(TecnicaDocking())
    ejecutor = EjecutorRegistro(registro, [Espia("1"), Espia("2", falla=True), Espia("3")])
    with pytest.raises(ErrorValidacion):
        ejecutor.registrar(datos_validos(), autor="ana")
    assert llamadas == ["1", "2"]


class TecnicaDinamicaDePrueba(Tecnica):
    """Plug-in de prueba (EC-07): una técnica nueva que se agrega sin modificar el núcleo."""

    tipo = "dinamica_molecular"
    etiqueta = "Dinámica molecular"

    def definiciones(self):
        return [DefinicionParametro("sistema", "Sistema", obligatorio=True),
                DefinicionParametro("paso_tiempo", "Paso de tiempo", unidad="fs", obligatorio=True)]

    def validar(self, parametros):
        return []

    def clave_coincidencia(self):
        return ["sistema"]

    def parametros_resumen(self):
        return ["sistema", "paso_tiempo"]


def test_cp11_ec07_una_tecnica_nueva_se_registra_sin_modificar_el_nucleo(repo, archivos):
    registro, ejecutor = construir_nucleo(repo, archivos)
    registro.registrar(TecnicaDinamicaDePrueba())  # único cambio: sumar el plug-in
    datos = datos_validos(tipo="dinamica_molecular", valores={"sistema": "Lisozima en agua", "paso_tiempo": "2"})
    e = ejecutor.registrar(datos, autor="ana")
    assert e.tipo == "dinamica_molecular"
    assert Parametro("paso_tiempo", "2", "fs") in e.parametros  # misma entidad, filas de parámetro con unidad
    with pytest.raises(PideConfirmacion):  # y la detección de duplicados usa la clave de la técnica nueva
        ejecutor.registrar(datos, autor="ana")
    assert registro.obtener("docking").tipo == "docking"  # el docking sigue funcionando


def test_cp12_la_fecha_de_realizacion_se_conserva(sistema):
    _, ejecutor = sistema
    e = ejecutor.registrar(datos_validos(fecha_realizacion=date(2026, 11, 2)), autor="ana")
    assert e.fecha_realizacion == date(2026, 11, 2)
