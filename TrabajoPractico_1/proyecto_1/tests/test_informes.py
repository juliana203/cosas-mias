import os
import shutil
import unittest

from modules.usuarios import UsuarioFinal
from modules.reclamo import Reclamo
from modules.informes import Informes, ReporteHTML, ReportePDF, CARPETA_REPORTES

# Un PNG 1x1 real en base64, para no depender de matplotlib en estos tests.
_PNG_1X1 = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4"
    "2mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def _reclamos_de_prueba():
    creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                            "jperez", "estudiante", "Clave123!", id_bd=1)
    r1 = Reclamo(creador, "El proyector no enciende", "maestranza")
    r1.id_reclamo = 1
    return [r1]


def _stats_de_prueba():
    return {"total": 1, "pendientes": 100.0, "en_proceso": 0.0, "resueltos": 0.0, "mediana_tiempos": 0}


def _graficos_de_prueba():
    return {"tor": _PNG_1X1, "tie": _PNG_1X1, "pf": _PNG_1X1}


class TestReporteHTML(unittest.TestCase):
    def tearDown(self):
        if os.path.isdir(CARPETA_REPORTES):
            shutil.rmtree(CARPETA_REPORTES)

    def test_genera_archivo_html_con_contenido(self):
        informes = Informes(ReporteHTML())
        ruta = informes.generar_reporte(_reclamos_de_prueba(), _stats_de_prueba(), "maestranza")
        self.assertTrue(os.path.exists(ruta))
        with open(ruta, encoding="utf-8") as f:
            contenido = f.read()
        self.assertIn("maestranza", contenido)
        self.assertIn("El proyector no enciende", contenido)

    def test_incluye_los_3_graficos(self):
        informes = Informes(ReporteHTML())
        ruta = informes.generar_reporte(_reclamos_de_prueba(), _stats_de_prueba(), "maestranza",
                                         graficos=_graficos_de_prueba())
        with open(ruta, encoding="utf-8") as f:
            contenido = f.read()
        self.assertEqual(contenido.count(_PNG_1X1), 3)

    def test_sin_graficos_no_explota(self):
        informes = Informes(ReporteHTML())
        ruta = informes.generar_reporte(_reclamos_de_prueba(), _stats_de_prueba(), "maestranza", graficos=None)
        self.assertTrue(os.path.exists(ruta))


class TestReportePDF(unittest.TestCase):
    def tearDown(self):
        if os.path.isdir(CARPETA_REPORTES):
            shutil.rmtree(CARPETA_REPORTES)

    def test_genera_archivo_pdf_real(self):
        informes = Informes(ReportePDF())
        ruta = informes.generar_reporte(_reclamos_de_prueba(), _stats_de_prueba(), "maestranza")
        self.assertTrue(os.path.exists(ruta))
        with open(ruta, "rb") as f:
            encabezado = f.read(4)
        self.assertEqual(encabezado, b"%PDF")

    def test_con_graficos_no_explota(self):
        informes = Informes(ReportePDF())
        ruta = informes.generar_reporte(_reclamos_de_prueba(), _stats_de_prueba(), "maestranza",
                                         graficos=_graficos_de_prueba())
        with open(ruta, "rb") as f:
            encabezado = f.read(4)
        self.assertEqual(encabezado, b"%PDF")


if __name__ == "__main__":
    unittest.main()