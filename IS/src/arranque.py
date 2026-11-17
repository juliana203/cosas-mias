"""Punto de arranque: el único lugar que arma los objetos concretos (inyección de dependencias)."""
from __future__ import annotations

from datetime import date, datetime

from .acceso_datos.archivos_en_memoria import AccesoArchivosEnMemoria
from .acceso_datos.repositorio_en_memoria import RepositorioExperimentosEnMemoria
from .dominio.entidades import Experimento, Parametro
from .dominio.pasos.detectar_duplicados import DetectarDuplicados
from .dominio.pasos.guardar_experimento import GuardarExperimento
from .dominio.pasos.validar_datos import ValidarDatos
from .dominio.registro_tecnicas import RegistroTecnicas
from .dominio.tecnica_docking import TecnicaDocking
from .servicios.ejecutor_registro import EjecutorRegistro
from .servicios.servicio_consulta import ServicioConsulta


def construir_nucleo(repositorio, archivos, registro_tecnicas=None):
    """Arma el núcleo del registro con tres pasos (Vincular documento queda fuera de alcance en el TP4)."""
    registro = registro_tecnicas or RegistroTecnicas()
    if registro_tecnicas is None:
        registro.registrar(TecnicaDocking())
    pasos = [ValidarDatos(repositorio), DetectarDuplicados(repositorio), GuardarExperimento(repositorio, archivos)]
    return registro, EjecutorRegistro(registro, pasos)


def cargar_datos_de_ejemplo(repositorio, archivos) -> None:
    ejemplo = Experimento(
        proyecto_id="P1",
        tipo="docking",
        autor="director.demo",
        fecha_hora=datetime(2026, 10, 1, 10, 0),
        fecha_realizacion=date(2026, 10, 1),
        parametros=[Parametro("proteina", "Proteasa HIV-1"), Parametro("ligando", "Indinavir"), Parametro("software", "AutoDock Vina")],
    )
    experimento_id = repositorio.guardar(experimento=ejemplo)
    ejemplo.ruta_pdb = archivos.guardar_pdb(experimento_id, b"HEADER EJEMPLO\nEND\n")
    repositorio.actualizar_rutas(ejemplo)


def crear_aplicacion():
    from .presentacion.rutas_registro import crear_app

    repositorio = RepositorioExperimentosEnMemoria({"P1": "Inhibidores de proteasa", "P2": "Lisozima"})
    archivos = AccesoArchivosEnMemoria()
    cargar_datos_de_ejemplo(repositorio, archivos)
    registro, ejecutor = construir_nucleo(repositorio, archivos)
    return crear_app(ejecutor, registro, ServicioConsulta(repositorio), autor="investigadora.demo")
