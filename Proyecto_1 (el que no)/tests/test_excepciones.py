import unittest

from modules import excepciones as exc


class TestJerarquiaDeExcepciones(unittest.TestCase):
    """Todas las excepciones de dominio deben colgar de AppError, y cada
    familia debe colgar de su excepción intermedia correspondiente."""

    def test_todas_heredan_de_apperror(self):
        clases = [
            exc.ClaustroInvalidoError, exc.EmailYaRegistradoError,
            exc.NombreUsuarioYaExisteError, exc.ContrasenaNoCoincideError,
            exc.UsuarioNoEncontradoError, exc.AutoAdhesionError,
            exc.AdhesionDuplicadaError, exc.TransicionEstadoInvalidaError,
            exc.ReclamoNoEncontradoError, exc.ImagenNoPermitidaError,
            exc.DepartamentoNoEncontradoError, exc.ContenidoVacioError,
            exc.TipoInformeNoSoportadoError, exc.GeneracionInformeError,
            exc.RolUsuarioDesconocidoError,
        ]
        for clase in clases:
            with self.subTest(clase=clase.__name__):
                self.assertTrue(issubclass(clase, exc.AppError))

    def test_familia_usuario(self):
        for clase in [exc.ClaustroInvalidoError, exc.EmailYaRegistradoError,
                      exc.NombreUsuarioYaExisteError, exc.ContrasenaNoCoincideError,
                      exc.UsuarioNoEncontradoError]:
            with self.subTest(clase=clase.__name__):
                self.assertTrue(issubclass(clase, exc.UsuarioError))

    def test_familia_reclamo(self):
        for clase in [exc.AutoAdhesionError, exc.AdhesionDuplicadaError,
                      exc.TransicionEstadoInvalidaError, exc.ReclamoNoEncontradoError,
                      exc.ImagenNoPermitidaError]:
            with self.subTest(clase=clase.__name__):
                self.assertTrue(issubclass(clase, exc.ReclamoError))

    def test_familia_informe(self):
        self.assertTrue(issubclass(exc.TipoInformeNoSoportadoError, exc.InformeError))
        self.assertTrue(issubclass(exc.GeneracionInformeError, exc.InformeError))

    def test_familia_persistencia(self):
        self.assertTrue(issubclass(exc.RolUsuarioDesconocidoError, exc.PersistenciaError))

    def test_se_puede_atrapar_por_la_clase_padre(self):
        try:
            raise exc.AutoAdhesionError()
        except exc.ReclamoError as e:
            self.assertIsInstance(e, exc.AutoAdhesionError)
        else:
            self.fail("no se atrapó la excepción")

    def test_se_puede_atrapar_por_la_raiz(self):
        try:
            raise exc.ClaustroInvalidoError("x", {"a", "b"})
        except exc.AppError:
            pass
        else:
            self.fail("no se atrapó la excepción")


class TestMensajesYAtributos(unittest.TestCase):
    """Cada excepción arma su propio mensaje y guarda los datos relevantes como atributos"""

    def test_usuario_no_encontrado_expone_id(self):
        e = exc.UsuarioNoEncontradoError(42)
        self.assertEqual(e.id_usuario, 42)
        self.assertIn("42", str(e))

    def test_reclamo_no_encontrado_expone_id(self):
        e = exc.ReclamoNoEncontradoError(7)
        self.assertEqual(e.id_reclamo, 7)
        self.assertIn("7", str(e))

    def test_email_ya_registrado_expone_email(self):
        e = exc.EmailYaRegistradoError("juli@fi.uner.edu.ar")
        self.assertEqual(e.email, "juli@fi.uner.edu.ar")
        self.assertIn("juli@fi.uner.edu.ar", str(e))

    def test_departamento_no_encontrado_expone_nombre(self):
        e = exc.DepartamentoNoEncontradoError("biblioteca")
        self.assertEqual(e.nombre, "biblioteca")

    def test_transicion_estado_invalida_expone_dias(self):
        e = exc.TransicionEstadoInvalidaError(dias_resolucion=99)
        self.assertEqual(e.dias_resolucion, 99)
        self.assertIn("1 y 15", str(e))

    def test_tipo_informe_no_soportado_expone_tipo_y_disponibles(self):
        e = exc.TipoInformeNoSoportadoError("EXCEL", ["HTML", "PDF"])
        self.assertEqual(e.tipo, "EXCEL")
        self.assertIn("HTML", e.tipos_disponibles)
        self.assertIn("PDF", e.tipos_disponibles)
        self.assertIn("EXCEL", str(e))

    def test_claustro_invalido_expone_claustro_y_validos(self):
        e = exc.ClaustroInvalidoError("x", {"estudiante", "docente", "PAyS"})
        self.assertEqual(e.claustro, "x")
        self.assertIn("estudiante", e.claustros_validos)

    def test_rol_usuario_desconocido_expone_rol(self):
        e = exc.RolUsuarioDesconocidoError("rol_raro")
        self.assertEqual(e.rol, "rol_raro")
        self.assertIn("rol_raro", str(e))

    def test_contrasena_no_coincide_mensaje_fijo(self):
        e = exc.ContrasenaNoCoincideError()
        self.assertIn("coinciden", str(e))

    def test_auto_adhesion_mensaje_fijo(self):
        e = exc.AutoAdhesionError()
        self.assertIn("propio reclamo", str(e))

    def test_adhesion_duplicada_mensaje_fijo(self):
        e = exc.AdhesionDuplicadaError()
        self.assertIn("ya está adherido", str(e))

    def test_contenido_vacio_mensaje_fijo(self):
        e = exc.ContenidoVacioError()
        self.assertIn("vacío", str(e))


if __name__ == "__main__":
    unittest.main()
