import unittest
from unittest.mock import MagicMock, patch

from modules.sistema import SubSubsistemaGestionReclamos
from modules.usuarios import UsuarioFinal, JefeDepartamento, SecretarioTecnico, Departamento
from modules.reclamo import Reclamo
from modules.excepciones import (
    EmailYaRegistradoError, NombreUsuarioYaExisteError,
    UsuarioNoEncontradoError, ReclamoNoEncontradoError, DepartamentoNoEncontradoError,
)


class MockRepo:
    """Repo genérico mockeado, sirve tanto para usuarios como para reclamos."""
    def __init__(self):
        self.guardar = MagicMock()
        self.obtener_por_filtro = MagicMock()
        self.obtener_por_id = MagicMock()
        self.actualizar = MagicMock()
        self.obtener_todos_por_filtro = MagicMock()
        self.asociar_reclamos_a_usuario = MagicMock()
        self.quitar_reclamos_a_usuario = MagicMock()


usuario_final = UsuarioFinal("A", "B", "a@b.com", "user", "estudiante", "pass", id_bd=1)
depto_soporte = Departamento("soporte informático", id=1)
depto_maestranza = Departamento("maestranza", id=2)
jefe_soporte = JefeDepartamento("J", "S", "j@s.com", "jefe", "pass", depto_soporte, id_bd=2)
jefe_maestranza = JefeDepartamento("J", "M", "j@m.com", "jefe2", "pass", depto_maestranza, id_bd=3)
secretario = SecretarioTecnico("S", "T", "s@t.com", "sec", "pass", id_bd=4)


class TestSubSubsistemaGestionReclamos(unittest.TestCase):
    def setUp(self):
        self.repo_usuarios = MockRepo()
        self.repo_reclamos = MockRepo()

        # ClasificadorReclamo intenta abrir un .pkl real en su __init__: lo mockeamos.
        self.patcher = patch("modules.sistema.ClasificadorReclamo")
        MockClasificador = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.mock_clasificador = MockClasificador.return_value
        self.mock_clasificador.clasificar.return_value = "soporte informático"

        self.sistema = SubSubsistemaGestionReclamos(self.repo_usuarios, self.repo_reclamos)

    # --- Usuarios ---

    def test_registrar_usuario_exitoso(self):
        self.repo_usuarios.obtener_por_filtro.return_value = None
        self.sistema.registrar_usuario("N", "A", "n@a.com", "nuevo", "docente", "pass")
        self.repo_usuarios.guardar.assert_called_once()

    def test_registrar_usuario_email_repetido(self):
        self.repo_usuarios.obtener_por_filtro.return_value = usuario_final
        with self.assertRaises(EmailYaRegistradoError):
            self.sistema.registrar_usuario("N", "A", "a@b.com", "otro", "docente", "pass")

    def test_registrar_usuario_nombre_usuario_repetido(self):
        # primer obtener_por_filtro (email) None, segundo (nombre_usuario) sí existe
        self.repo_usuarios.obtener_por_filtro.side_effect = [None, usuario_final]
        with self.assertRaises(NombreUsuarioYaExisteError):
            self.sistema.registrar_usuario("N", "A", "n@a.com", "user", "docente", "pass")

    def test_buscar_usuario_inexistente(self):
        self.repo_usuarios.obtener_por_filtro.return_value = None
        with self.assertRaises(UsuarioNoEncontradoError):
            self.sistema.buscar_usuario("no_existe")

    # --- Creación / búsqueda de reclamos ---

    def test_crear_reclamo_usuario_inexistente(self):
        self.repo_usuarios.obtener_por_filtro.return_value = None
        with self.assertRaises(UsuarioNoEncontradoError):
            self.sistema.crear_reclamo(usuario_final, "Test")

    def test_crear_reclamo_exitoso(self):
        self.repo_usuarios.obtener_por_filtro.return_value = usuario_final
        self.mock_clasificador.clasificar.return_value = "maestranza"
        reclamo = self.sistema.crear_reclamo(usuario_final, "Hay basura")
        self.assertEqual(reclamo.departamento, "maestranza")
        self.repo_reclamos.guardar.assert_called_once()

    def test_buscar_reclamo_por_id_inexistente(self):
        self.repo_reclamos.obtener_por_id.return_value = None
        with self.assertRaises(ReclamoNoEncontradoError):
            self.sistema.buscar_reclamo_por_id(99)

    # --- Adhesión ---

    def test_adherir_a_reclamo_ya_adherido_no_llama_de_nuevo(self):
        reclamo_mock = MagicMock(Reclamo, adherentes=[usuario_final], id_reclamo=1)
        self.repo_reclamos.obtener_por_id.return_value = reclamo_mock
        self.sistema.adherir_a_reclamo(usuario_final, 1)
        self.repo_usuarios.asociar_reclamos_a_usuario.assert_not_called()

    def test_adherir_a_reclamo_exitoso(self):
        reclamo_mock = MagicMock(Reclamo, adherentes=[], id_reclamo=1)
        self.repo_reclamos.obtener_por_id.return_value = reclamo_mock
        self.sistema.adherir_a_reclamo(usuario_final, 1)
        self.repo_usuarios.asociar_reclamos_a_usuario.assert_called_once()
        reclamo_mock.agregar_adherentes.assert_called_once_with(usuario_final)

    def test_adherir_usuario_sin_id_lo_busca_por_nombre(self):
        usuario_fantasma = UsuarioFinal("A", "B", "a@b.com", "user", "estudiante", "pass")
        usuario_real = UsuarioFinal("A", "B", "a@b.com", "user", "estudiante", "pass", id_bd=1)
        reclamo_mock = MagicMock(Reclamo, adherentes=[], id_reclamo=1)
        self.repo_reclamos.obtener_por_id.return_value = reclamo_mock
        self.repo_usuarios.obtener_por_filtro.return_value = usuario_real

        self.sistema.adherir_a_reclamo(usuario_fantasma, 1)

        self.repo_usuarios.asociar_reclamos_a_usuario.assert_called_once_with(
            id_usuario=1, id_reclamo=1,
        )

    def test_adherir_usuario_no_registrado(self):
        usuario_sin_id = UsuarioFinal("B", "B", "b@b.com", "user_b", "estudiante", "pass")
        self.repo_usuarios.obtener_por_filtro.return_value = None
        with self.assertRaises(UsuarioNoEncontradoError):
            self.sistema.adherir_a_reclamo(usuario_sin_id, 1)

    # --- Cambio de estado ---

    def test_cambiar_estado_permiso_denegado(self):
        reclamo = Reclamo(usuario_final, "Red lenta", "soporte informático")
        reclamo.id_reclamo = 1
        self.repo_reclamos.obtener_por_id.return_value = reclamo
        with self.assertRaisesRegex(Exception, "Permiso denegado"):
            self.sistema.cambiar_estado_reclamo(jefe_maestranza, 1, "resuelto")

    def test_cambiar_estado_exitoso(self):
        reclamo = Reclamo(usuario_final, "Red lenta", "soporte informático")
        reclamo.id_reclamo = 1
        self.repo_reclamos.obtener_por_id.return_value = reclamo
        self.sistema.cambiar_estado_reclamo(jefe_soporte, 1, "en proceso", 5)
        self.assertEqual(reclamo.estado, "en proceso")
        self.repo_reclamos.actualizar.assert_called_once_with(reclamo)

    # --- Listados ---

    def test_listar_reclamos_usuario_inexistente(self):
        self.repo_usuarios.obtener_por_filtro.return_value = None
        with self.assertRaises(UsuarioNoEncontradoError):
            self.sistema.listar_reclamos_usuario(usuario_final)

    def test_listar_reclamos_usuario_filtra_por_id_bd(self):
        self.repo_usuarios.obtener_por_filtro.return_value = usuario_final
        self.sistema.listar_reclamos_usuario(usuario_final)
        self.repo_reclamos.obtener_todos_por_filtro.assert_called_once_with(id_usuario_creador=1)

    def test_buscar_reclamos_pendientes_todos(self):
        self.repo_reclamos.obtener_todos_por_filtro.return_value = ["algo"]
        resultado = self.sistema.buscar_reclamos_pendientes_todos()
        self.assertEqual(len(resultado), 1)
        self.repo_reclamos.obtener_todos_por_filtro.assert_called_once_with(estado="pendiente")

    def test_buscar_reclamos_similares_indefinido_devuelve_vacio(self):
        self.mock_clasificador.clasificar.return_value = "indefinido"
        resultado = self.sistema.buscar_reclamos_similares("reclamo raro")
        self.assertEqual(resultado, [])

    # --- Derivación ---

    def test_derivar_reclamo_permiso_denegado(self):
        with self.assertRaisesRegex(Exception, "Solo el Secretario Técnico"):
            self.sistema.derivar_reclamo(jefe_soporte, 1, "maestranza")

    def test_derivar_reclamo_departamento_invalido(self):
        with self.assertRaises(DepartamentoNoEncontradoError):
            self.sistema.derivar_reclamo(secretario, 1, "departamento inventado")

    def test_derivar_reclamo_exitoso(self):
        reclamo = Reclamo(usuario_final, "Red lenta", "soporte informático")
        reclamo.id_reclamo = 1
        self.repo_reclamos.obtener_por_id.return_value = reclamo
        self.sistema.derivar_reclamo(secretario, 1, "maestranza")
        self.assertEqual(reclamo.departamento, "maestranza")
        self.repo_reclamos.actualizar.assert_called_once_with(reclamo)


if __name__ == "__main__":
    unittest.main()
