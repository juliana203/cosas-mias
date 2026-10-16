import unittest
from unittest.mock import MagicMock, patch

from modules.gestores import GestorUsuario, GestorReclamos
from modules.usuarios import UsuarioFinal, Departamento
from modules.reclamos import Reclamo, EstadoReclamo
from modules.excepciones import (
    ContrasenaNoCoincideError, EmailYaRegistradoError, NombreUsuarioYaExisteError,
    AutoAdhesionError, AdhesionDuplicadaError, ReclamoNoEncontradoError,
    UsuarioNoEncontradoError, DepartamentoNoEncontradoError, ImagenNoPermitidaError,
    TransicionEstadoInvalidaError,
)

class TestGestorUsuarioInscribiruser(unittest.TestCase):
    def setUp(self):
        self.dao_usuarios = MagicMock()
        self.login_manager = MagicMock()
        self.gestor = GestorUsuario(self.login_manager, self.dao_usuarios)

    def _datos_validos(self):
        return {
            "nombre": "Juliana", "apellido": "Perez", "email": "juliana@fi.uner.edu.ar",
            "nombre_usuario": "jperez", "claustro": "estudiante",
            "contrasena": "Clave123!", "contrasena_repetida": "Clave123!",
        }

    def test_contrasenas_no_coinciden(self):
        datos = self._datos_validos()
        datos["contrasena_repetida"] = "OtraClave!"
        with self.assertRaises(ContrasenaNoCoincideError):
            self.gestor.inscribiruser(datos)
        self.dao_usuarios.inscribiruser.assert_not_called()

    def test_email_ya_registrado(self):
        self.dao_usuarios.filtrarporemail.return_value = MagicMock()  # ya hay alguien con ese email
        with self.assertRaises(EmailYaRegistradoError):
            self.gestor.inscribiruser(self._datos_validos())

    def test_nombre_usuario_ya_existe(self):
        self.dao_usuarios.filtrarporemail.return_value = None
        self.dao_usuarios.filtrarpornombreusuario.return_value = MagicMock()
        with self.assertRaises(NombreUsuarioYaExisteError):
            self.gestor.inscribiruser(self._datos_validos())

    def test_alta_exitosa_llama_al_dao_con_usuariofinal_correcto(self):
        self.dao_usuarios.filtrarporemail.return_value = None
        self.dao_usuarios.filtrarpornombreusuario.return_value = None
        self.dao_usuarios.inscribiruser.side_effect = lambda u: u

        resultado = self.gestor.inscribiruser(self._datos_validos())

        self.dao_usuarios.inscribiruser.assert_called_once()
        usuario_pasado = self.dao_usuarios.inscribiruser.call_args[0][0]
        self.assertIsInstance(usuario_pasado, UsuarioFinal)
        self.assertEqual(usuario_pasado.nombre_usuario, "jperez")
        self.assertEqual(usuario_pasado.claustro, "estudiante")
        self.assertIsInstance(resultado, UsuarioFinal)


class TestGestorUsuarioLogin(unittest.TestCase):
    def setUp(self):
        self.dao_usuarios = MagicMock()
        self.login_manager = MagicMock()
        self.gestor = GestorUsuario(self.login_manager, self.dao_usuarios)
        self.usuario = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                                     "jperez", "estudiante", "Clave123!", id_bd=1)

    @patch("modules.gestores.login_user")
    def test_login_exitoso_llama_a_login_user(self, mock_login_user):
        self.dao_usuarios.filtrarpornombreusuario.return_value = self.usuario
        resultado = self.gestor.login("jperez", "Clave123!")
        self.assertEqual(resultado, self.usuario)
        mock_login_user.assert_called_once_with(self.usuario)

    @patch("modules.gestores.login_user")
    def test_login_contrasena_incorrecta_no_inicia_sesion(self, mock_login_user):
        self.dao_usuarios.filtrarpornombreusuario.return_value = self.usuario
        resultado = self.gestor.login("jperez", "clave_incorrecta")
        self.assertIsNone(resultado)
        mock_login_user.assert_not_called()

    @patch("modules.gestores.login_user")
    def test_login_usuario_inexistente_no_inicia_sesion(self, mock_login_user):
        self.dao_usuarios.filtrarpornombreusuario.return_value = None
        resultado = self.gestor.login("no_existe", "cualquier_clave")
        self.assertIsNone(resultado)
        mock_login_user.assert_not_called()

    @patch("modules.gestores.logout_user")
    def test_logout_llama_a_logout_user(self, mock_logout_user):
        self.gestor.logout()
        mock_logout_user.assert_called_once()


class TestGestorUsuarioAutorizacion(unittest.TestCase):
    def setUp(self):
        self.dao_usuarios = MagicMock()
        self.login_manager = MagicMock()
        self.gestor = GestorUsuario(self.login_manager, self.dao_usuarios)

    def test_se_requiere_login_devuelve_login_required(self):
        from modules.gestores import login_required
        self.assertIs(self.gestor.se_requiere_login(), login_required)

    @patch("modules.gestores.current_user")
    def test_rol_requerido_permite_paso_si_el_rol_coincide(self, mock_current_user):
        mock_current_user.is_authenticated = True
        mock_current_user.rol = "jefe_departamento"

        vista_mock = MagicMock(return_value="ok")
        vista_protegida = self.gestor.rol_requerido(["jefe_departamento", "secretario_tecnico"])(vista_mock)

        resultado = vista_protegida()
        self.assertEqual(resultado, "ok")
        vista_mock.assert_called_once()

    @patch("modules.gestores.abort")
    @patch("modules.gestores.current_user")
    def test_rol_requerido_bloquea_con_403_si_el_rol_no_coincide(self, mock_current_user, mock_abort):
        mock_current_user.is_authenticated = True
        mock_current_user.rol = "usuario_final"
        mock_abort.side_effect = Exception("403 simulado")

        vista_mock = MagicMock(return_value="ok")
        vista_protegida = self.gestor.rol_requerido(["jefe_departamento"])(vista_mock)

        with self.assertRaises(Exception):
            vista_protegida()
        mock_abort.assert_called_once_with(403)
        vista_mock.assert_not_called()

    @patch("modules.gestores.abort")
    @patch("modules.gestores.current_user")
    def test_rol_requerido_bloquea_con_401_si_no_hay_sesion(self, mock_current_user, mock_abort):
        mock_current_user.is_authenticated = False
        mock_abort.side_effect = Exception("401 simulado")

        vista_mock = MagicMock(return_value="ok")
        vista_protegida = self.gestor.rol_requerido(["jefe_departamento"])(vista_mock)

        with self.assertRaises(Exception):
            vista_protegida()
        mock_abort.assert_called_once_with(401)
        vista_mock.assert_not_called()


class TestGestorReclamosCrearReclamo(unittest.TestCase):
    def setUp(self):
        self.dao_usuarios = MagicMock()
        self.dao_reclamos = MagicMock()
        self.clasificador = MagicMock()
        self.analitica = MagicMock()
        self.gestor = GestorReclamos(self.dao_usuarios, self.dao_reclamos,
                                      self.clasificador, self.analitica)
        self.creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                                     "jperez", "estudiante", "Clave123!", id_bd=1)
        self.depto = Departamento("maestranza", id=1)

    def test_crea_reclamo_nuevo_cuando_no_hay_similares(self):
        self.clasificador.clasificar.return_value = "maestranza"
        self.dao_reclamos.obtener_departamento_por_nombre.return_value = self.depto
        self.dao_reclamos.get_reclamo_pordepto.return_value = []  # nada activo -> no hay similares
        self.dao_reclamos.guardar_reclamo.side_effect = lambda r: r

        resultado = self.gestor.crear_reclamo({
            "usuario_creador": self.creador,
            "contenido": "El proyector no enciende",
        })

        self.assertEqual(resultado["similares"], [])
        self.assertEqual(resultado["mensaje"], "Reclamo creado")
        self.assertIsNotNone(resultado["reclamo"])
        self.dao_reclamos.guardar_reclamo.assert_called_once()

    def test_con_imagen_valida_se_guarda_y_se_asocia_al_reclamo(self):
        self.clasificador.clasificar.return_value = "maestranza"
        self.dao_reclamos.obtener_departamento_por_nombre.return_value = self.depto
        self.dao_reclamos.get_reclamo_pordepto.return_value = []
        self.dao_reclamos.guardar_reclamo.side_effect = lambda r: r

        imagen_valida = MagicMock()
        imagen_valida.filename = "foto.jpg"

        with patch.object(self.gestor, "guardar_imagen", return_value="uploads/abc_foto.jpg") as mock_guardar:
            resultado = self.gestor.crear_reclamo({
                "usuario_creador": self.creador,
                "contenido": "El proyector no enciende",
                "imagen": imagen_valida,
            })

        mock_guardar.assert_called_once_with(imagen_valida)
        self.assertEqual(resultado["ruta_imagen"], "uploads/abc_foto.jpg")
        self.assertEqual(resultado["reclamo"].ruta_imagen, "uploads/abc_foto.jpg")

    def test_sin_imagen_ruta_imagen_queda_en_none(self):
        self.clasificador.clasificar.return_value = "maestranza"
        self.dao_reclamos.obtener_departamento_por_nombre.return_value = self.depto
        self.dao_reclamos.get_reclamo_pordepto.return_value = []
        self.dao_reclamos.guardar_reclamo.side_effect = lambda r: r

        resultado = self.gestor.crear_reclamo({
            "usuario_creador": self.creador,
            "contenido": "El proyector no enciende",
        })

        self.assertIsNone(resultado["ruta_imagen"])
        self.assertIsNone(resultado["reclamo"].ruta_imagen)


    def test_reclamos_similares_se_devuelven_sin_crear_ni_adherir(self):
        self.clasificador.clasificar.return_value = "maestranza"
        self.dao_reclamos.obtener_departamento_por_nombre.return_value = self.depto

        otro_usuario = UsuarioFinal("Marco", "Ruiz", "marco@fi.uner.edu.ar",
                                     "mruiz", "docente", "Clave456!", id_bd=2)
        similar_1 = Reclamo(otro_usuario, "El proyector del aula 3 no enciende",
                             self.depto, id_reclamo=50)
        similar_2 = Reclamo(otro_usuario, "el proyector del aula 3 no prende",
                             self.depto, id_reclamo=51)
        self.dao_reclamos.get_reclamo_pordepto.return_value = [similar_1, similar_2]

        resultado = self.gestor.crear_reclamo({
            "usuario_creador": self.creador,
            "contenido": "El proyector del aula 3 no funciona",
        })

        self.assertEqual(len(resultado["similares"]), 2)
        self.assertIsNone(resultado["reclamo"])
        self.assertIsNone(resultado["mensaje"])
        self.dao_reclamos.guardar_reclamo.assert_not_called()
        self.dao_reclamos.actualizar.assert_not_called()

    def test_imagen_con_formato_no_permitido_lanza_excepcion(self):
        self.clasificador.clasificar.return_value = "maestranza"
        self.dao_reclamos.obtener_departamento_por_nombre.return_value = self.depto
        self.dao_reclamos.get_reclamo_pordepto.return_value = []

        imagen_falsa = MagicMock()
        imagen_falsa.filename = "virus.exe"

        with self.assertRaises(ImagenNoPermitidaError):
            self.gestor.crear_reclamo({
                "usuario_creador": self.creador,
                "contenido": "algo",
                "imagen": imagen_falsa,
            })


class TestGestorReclamosCrearReclamoForzado(unittest.TestCase):
    """El usuario vio los similares y decidió crear el suyo de todas formas"""

    def setUp(self):
        self.dao_usuarios = MagicMock()
        self.dao_reclamos = MagicMock()
        self.gestor = GestorReclamos(self.dao_usuarios, self.dao_reclamos,
                                      clasificador=MagicMock(), analitica=MagicMock())
        self.creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                                     "jperez", "estudiante", "Clave123!", id_bd=1)
        self.depto = Departamento("maestranza", id=1)

    def test_crea_y_persiste_directamente(self):
        self.dao_reclamos.guardar_reclamo.side_effect = lambda r: r

        reclamo = self.gestor.crear_reclamo_forzado(self.creador, "Un reclamo distinto", self.depto)

        self.assertEqual(reclamo.contenido, "Un reclamo distinto")
        self.assertEqual(reclamo.departamento, self.depto)
        self.dao_reclamos.guardar_reclamo.assert_called_once()


class TestGestorReclamosAdhesion(unittest.TestCase):
    def setUp(self):
        self.dao_usuarios = MagicMock()
        self.dao_reclamos = MagicMock()
        self.gestor = GestorReclamos(self.dao_usuarios, self.dao_reclamos,
                                      clasificador=MagicMock(), analitica=MagicMock())
        self.creador = UsuarioFinal("Juliana", "Perez", "juliana@fi.uner.edu.ar",
                                     "jperez", "estudiante", "Clave123!", id_bd=1)
        self.otro = UsuarioFinal("Marco", "Ruiz", "marco@fi.uner.edu.ar",
                                  "mruiz", "docente", "Clave456!", id_bd=2)
        self.depto = Departamento("maestranza", id=1)
        self.reclamo = Reclamo(self.creador, "El proyector no enciende", self.depto, id_reclamo=100)

    def test_creador_no_puede_adherirse_a_su_propio_reclamo(self):
        self.dao_reclamos.obtener_por_id.return_value = self.reclamo
        self.dao_usuarios.obtener_por_id.return_value = self.creador
        with self.assertRaises(AutoAdhesionError):
            self.gestor.adherirse_reclamo(100, self.creador.id_bd)
        self.dao_reclamos.actualizar.assert_not_called()

    def test_otro_usuario_puede_adherirse_y_se_persiste(self):
        self.dao_reclamos.obtener_por_id.return_value = self.reclamo
        self.dao_usuarios.obtener_por_id.return_value = self.otro
        self.gestor.adherirse_reclamo(100, self.otro.id_bd)
        self.assertEqual(len(self.reclamo.adherentes), 1)
        self.dao_reclamos.actualizar.assert_called_once_with(self.reclamo)

    def test_no_se_puede_adherir_dos_veces(self):
        self.reclamo.agregar_adherente(self.otro)
        self.dao_reclamos.obtener_por_id.return_value = self.reclamo
        self.dao_usuarios.obtener_por_id.return_value = self.otro
        with self.assertRaises(AdhesionDuplicadaError):
            self.gestor.adherirse_reclamo(100, self.otro.id_bd)

    def test_adherirse_con_usuario_inexistente(self):
        self.dao_reclamos.obtener_por_id.return_value = self.reclamo
        self.dao_usuarios.obtener_por_id.return_value = None
        with self.assertRaises(UsuarioNoEncontradoError):
            self.gestor.adherirse_reclamo(100, 999)

    def test_desadherirse_quita_al_usuario_y_persiste(self):
        self.reclamo.agregar_adherente(self.otro)
        self.dao_reclamos.obtener_por_id.return_value = self.reclamo
        self.gestor.desadherirse_reclamo(100, self.otro.id_bd)
        self.assertEqual(len(self.reclamo.adherentes), 0)
        self.dao_reclamos.actualizar.assert_called_once_with(self.reclamo)


class TestGestorReclamosCambiarEstado(unittest.TestCase):
    def setUp(self):
        self.dao_usuarios = MagicMock()
        self.dao_reclamos = MagicMock()
        self.gestor = GestorReclamos(self.dao_usuarios, self.dao_reclamos,
                                      clasificador=MagicMock(), analitica=MagicMock())
        creador = UsuarioFinal("A", "B", "a@b.com", "ab", "estudiante", "pass", id_bd=1)
        self.depto = Departamento("maestranza", id=1)
        self.reclamo = Reclamo(creador, "x", self.depto, id_reclamo=1)

    def test_cambiar_estado_exitoso(self):
        self.dao_reclamos.obtener_por_id.return_value = self.reclamo
        self.gestor.cambiar_estado_reclamo(1, EstadoReclamo.EN_PROCESO, dias_resolucion=5)
        self.assertEqual(self.reclamo.estado, EstadoReclamo.EN_PROCESO)
        self.dao_reclamos.actualizar.assert_called_once_with(self.reclamo)

    def test_dias_invalidos_propaga_la_excepcion_de_dominio_sin_persistir(self):
        self.dao_reclamos.obtener_por_id.return_value = self.reclamo
        with self.assertRaises(TransicionEstadoInvalidaError):
            self.gestor.cambiar_estado_reclamo(1, EstadoReclamo.EN_PROCESO, dias_resolucion=99)
        self.dao_reclamos.actualizar.assert_not_called()


class TestGestorReclamosDerivar(unittest.TestCase):
    def setUp(self):
        self.dao_usuarios = MagicMock()
        self.dao_reclamos = MagicMock()
        self.gestor = GestorReclamos(self.dao_usuarios, self.dao_reclamos,
                                      clasificador=MagicMock(), analitica=MagicMock())
        creador = UsuarioFinal("A", "B", "a@b.com", "ab", "estudiante", "pass", id_bd=1)
        self.depto_actual = Departamento("maestranza", id=1)
        self.reclamo = Reclamo(creador, "x", self.depto_actual, id_reclamo=1)

    def test_derivar_exitoso(self):
        nuevo_depto = Departamento("soporte informático", id=2)
        self.dao_reclamos.obtener_por_id.return_value = self.reclamo
        self.dao_reclamos.obtener_departamento_por_nombre.return_value = nuevo_depto

        self.gestor.derivar_reclamo(1, "soporte informático")

        self.assertEqual(self.reclamo.departamento, nuevo_depto)
        self.dao_reclamos.actualizar.assert_called_once_with(self.reclamo)

    def test_derivar_a_departamento_inexistente(self):
        self.dao_reclamos.obtener_por_id.return_value = self.reclamo
        self.dao_reclamos.obtener_departamento_por_nombre.return_value = None
        with self.assertRaises(DepartamentoNoEncontradoError):
            self.gestor.derivar_reclamo(1, "departamento_que_no_existe")


class TestGestorReclamosGenerarReporte(unittest.TestCase):
    def test_orquesta_los_pasos_en_el_orden_correcto(self):
        dao_usuarios = MagicMock()
        dao_reclamos = MagicMock()
        analitica = MagicMock()
        gestor = GestorReclamos(dao_usuarios, dao_reclamos, clasificador=MagicMock(), analitica=analitica)
        datos_falsos = MagicMock()

        analitica.calculardatos.return_value = datos_falsos
        analitica.generar_grafica_tor.return_value = "tor"
        analitica.generar_grafica_tie.return_value = "tie"
        analitica.generar_grafica_pa.return_value = "pa"
        analitica.generar_reporte.return_value = "informe_final"

        lista_reclamos = [MagicMock()]
        resultado = gestor.generar_reporte("PDF", lista_reclamos)

        analitica.calculardatos.assert_called_once_with(lista_reclamos)
        analitica.generar_grafica_tor.assert_called_once_with(datos_falsos)
        analitica.generar_grafica_tie.assert_called_once_with(datos_falsos)
        analitica.generar_grafica_pa.assert_called_once_with(datos_falsos)
        analitica.generar_reporte.assert_called_once_with(datos_falsos, "tor", "tie", "pa", "PDF")
        self.assertEqual(resultado, "informe_final")


class TestGestorReclamosUtilidades(unittest.TestCase):
    def setUp(self):
        self.dao_usuarios = MagicMock()
        self.dao_reclamos = MagicMock()
        self.gestor = GestorReclamos(self.dao_usuarios, self.dao_reclamos,
                                      clasificador=MagicMock(), analitica=MagicMock())

    def test_guardar_imagen_devuelve_ruta_relativa_a_static(self):
        """
        guardar_imagen() debe devolver algo usable directo como
        url_for('static', filename=ruta) — es decir, SIN el prefijo 'static/'
        """
        import tempfile, os

        archivo_falso = MagicMock()
        archivo_falso.filename = "foto de prueba.jpg"
        archivo_falso.save = MagicMock()

        directorio_original = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            try:
                ruta = self.gestor.guardar_imagen(archivo_falso)
            finally:
                os.chdir(directorio_original)

        self.assertTrue(ruta.startswith("uploads/"))
        self.assertNotIn("static/", ruta)  # no debe incluir el prefijo static/
        self.assertTrue(ruta.endswith(".jpg"))
        archivo_falso.save.assert_called_once()

    def test_allowed_file_extensiones_permitidas(self):
        for nombre in ["foto.png", "foto.JPG", "foto.jpeg", "foto.gif"]:
            with self.subTest(nombre=nombre):
                self.assertTrue(self.gestor.allowed_file(nombre))

    def test_allowed_file_extension_no_permitida(self):
        self.assertFalse(self.gestor.allowed_file("virus.exe"))

    def test_allowed_file_sin_extension(self):
        self.assertFalse(self.gestor.allowed_file("archivo_sin_extension"))

    def test_comparar_contenidos_similares(self):
        self.assertTrue(self.gestor.comparar(
            "El proyector del aula 3 no enciende",
            "el PROYECTOR del aula 3 no enciende",
        ))

    def test_comparar_contenidos_distintos(self):
        self.assertFalse(self.gestor.comparar(
            "El proyector del aula 3 no enciende",
            "No puedo inscribirme al final de la materia",
        ))

    def test_obtener_reclamo_inexistente_lanza_excepcion(self):
        self.dao_reclamos.obtener_por_id.return_value = None
        with self.assertRaises(ReclamoNoEncontradoError):
            self.gestor.obtener_reclamo(999)

    def test_obtener_reclamo_existente(self):
        reclamo_falso = MagicMock()
        self.dao_reclamos.obtener_por_id.return_value = reclamo_falso
        self.assertEqual(self.gestor.obtener_reclamo(1), reclamo_falso)

    def test_get_reclamos_pendientes_filtra_por_estado(self):
        creador = UsuarioFinal("A", "B", "a@b.com", "ab", "estudiante", "pass", id_bd=1)
        depto = Departamento("maestranza", id=1)
        r_pendiente = Reclamo(creador, "x", depto, id_reclamo=1)
        r_en_proceso = Reclamo(creador, "y", depto, id_reclamo=2)
        r_en_proceso.cambiar_estado(EstadoReclamo.EN_PROCESO, dias_resolucion=3)
        self.dao_reclamos.get_reclamos_completo.return_value = [r_pendiente, r_en_proceso]

        resultado = self.gestor.get_reclamos_pendientes()

        self.assertEqual(resultado, [r_pendiente])


if __name__ == "__main__":
    unittest.main()
