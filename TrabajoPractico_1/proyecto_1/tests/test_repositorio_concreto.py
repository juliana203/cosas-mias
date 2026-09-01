import unittest
from unittest.mock import MagicMock, patch
import datetime

from modules.repositorio_concreto import RepositorioUsuariosSQLAlchemy, RepositorioReclamosSQLAlchemy
from modules.usuarios import UsuarioFinal, JefeDepartamento
from modules.reclamo import Reclamo
from modules.modelos_db import ModeloUsuario, ModeloReclamo, Base


def mock_modelo_usuario(id, rol="usuario_final", depto=None):
    return ModeloUsuario(
        id=id, nombre="N", apellido="A", email=f"e{id}@t.com",
        nombre_usuario=f"user{id}", claustro="estudiante", contrasena="hash",
        rol=rol, departamento_asignado=depto,
    )


def mock_modelo_reclamo(id, id_creador):
    return ModeloReclamo(
        id=id, contenido="Contenido", departamento="maestranza",
        timestamp=datetime.datetime.now(), estado="pendiente",
        id_usuario_creador=id_creador,
    )


class TestRepositorioUsuariosSQLAlchemy(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        with patch.object(Base.metadata, "create_all"):
            self.repo = RepositorioUsuariosSQLAlchemy(self.mock_session)
        self.mock_query = self.mock_session.query.return_value
        self.mock_filter = self.mock_query.filter_by.return_value

    def test_map_modelo_a_entidad_jefe(self):
        modelo = mock_modelo_usuario(1, rol="jefe_departamento", depto="soporte informático")
        entidad = self.repo._RepositorioUsuariosSQLAlchemy__map_modelo_a_entidad(modelo)
        self.assertIsInstance(entidad, JefeDepartamento)
        self.assertEqual(entidad.departamento_asignado.nombre, "soporte informático")

    def test_map_modelo_a_entidad_usuario_final(self):
        modelo = mock_modelo_usuario(1, rol="usuario_final")
        entidad = self.repo._RepositorioUsuariosSQLAlchemy__map_modelo_a_entidad(modelo)
        self.assertIsInstance(entidad, UsuarioFinal)

    def test_map_modelo_a_entidad_no_re_hashea_la_contrasena(self):
        modelo = mock_modelo_usuario(1, rol="usuario_final")
        modelo.contrasena = "hash_ya_guardado"
        entidad = self.repo._RepositorioUsuariosSQLAlchemy__map_modelo_a_entidad(modelo)
        self.assertEqual(entidad.contrasena, "hash_ya_guardado")

    def test_guardar_usuario_existente(self):
        entidad = UsuarioFinal("A", "B", "a@b.com", "user", "estudiante", "pass")
        mock_modelo_existente = MagicMock(rol="usuario_final", id=1, nombre="N", apellido="A",
                                           email="e@t.com", nombre_usuario="user", claustro="docente",
                                           contrasena="hash", departamento_asignado=None)
        self.mock_filter.first.side_effect = [mock_modelo_existente, None]
        with self.assertRaises(ValueError):
            self.repo.guardar(entidad)

    def test_guardar_exitoso(self):
        entidad = UsuarioFinal("A", "B", "a@b.com", "user", "estudiante", "pass")
        self.mock_filter.first.return_value = None
        self.mock_session.refresh.side_effect = lambda modelo: setattr(modelo, "id", 1)
        self.repo.guardar(entidad)
        self.mock_session.add.assert_called_once()
        self.assertEqual(entidad.id_bd, 1)

    def test_obtener_por_id_no_encontrado(self):
        self.mock_session.get.return_value = None
        self.assertIsNone(self.repo.obtener_por_id(99))

    def test_actualizar_usuario_no_encontrado(self):
        entidad = UsuarioFinal("A", "B", "a@b.com", "user", "estudiante", "pass")
        self.mock_filter.first.return_value = None
        with self.assertRaises(ValueError):
            self.repo.actualizar(entidad)

    def test_eliminar_usuario_no_encontrado(self):
        self.mock_session.get.return_value = None
        with self.assertRaises(ValueError):
            self.repo.eliminar(99)

    def test_asociar_reclamos_a_usuario_usuario_no_existe(self):
        self.mock_session.get.side_effect = [None, mock_modelo_reclamo(id=1, id_creador=1)]
        with self.assertRaisesRegex(ValueError, "El usuario no existe."):
            self.repo.asociar_reclamos_a_usuario(id_usuario=99, id_reclamo=1)

    def test_asociar_reclamos_a_usuario_exitoso(self):
        mock_user = mock_modelo_usuario(id=1)
        mock_user.reclamos_adheridos = []
        mock_reclamo = mock_modelo_reclamo(id=1, id_creador=1)
        self.mock_session.get.side_effect = [mock_user, mock_reclamo]

        self.repo.asociar_reclamos_a_usuario(id_usuario=1, id_reclamo=1)

        self.assertIn(mock_reclamo, mock_user.reclamos_adheridos)
        self.mock_session.commit.assert_called_once()


class TestRepositorioReclamosSQLAlchemy(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        with patch.object(Base.metadata, "create_all"):
            self.repo = RepositorioReclamosSQLAlchemy(self.mock_session)
        self.mock_query = self.mock_session.query.return_value
        self.mock_repo_usuarios = self.repo._RepositorioReclamosSQLAlchemy__repo_usuarios
        self.mock_repo_usuarios.obtener_por_id = MagicMock(
            return_value=UsuarioFinal("C", "R", "c@r.com", "creador", "estudiante", "pass", id_bd=1)
        )

    def test_map_modelo_a_entidad_inconsistencia_usuario(self):
        self.mock_repo_usuarios.obtener_por_id.return_value = None
        modelo = mock_modelo_reclamo(id=1, id_creador=99)
        with self.assertRaisesRegex(Exception, "Inconsistencia"):
            self.repo._RepositorioReclamosSQLAlchemy__map_modelo_a_entidad(modelo)

    def test_map_modelo_a_entidad_con_adherentes(self):
        modelo = mock_modelo_reclamo(id=1, id_creador=1)
        mock_adherente_modelo = mock_modelo_usuario(id=2)
        modelo.adherentes = [mock_adherente_modelo]
        mock_adherente_entidad = UsuarioFinal("A", "D", "a@d.com", "adh", "estudiante", "pass", id_bd=2)
        self.mock_repo_usuarios._RepositorioUsuariosSQLAlchemy__map_modelo_a_entidad = MagicMock(
            return_value=mock_adherente_entidad
        )
        entidad = self.repo._RepositorioReclamosSQLAlchemy__map_modelo_a_entidad(modelo)
        self.assertEqual(entidad.numero_adherentes, 1)

    def test_map_entidad_a_modelo_usuario_no_existe(self):
        entidad = Reclamo(UsuarioFinal("A", "B", "c@d.com", "fake", "estudiante", "p"), "contenido", "maestranza")
        self.mock_query.filter_by.return_value.first.return_value = None
        with self.assertRaisesRegex(ValueError, "no existe en la base de datos"):
            self.repo._RepositorioReclamosSQLAlchemy__map_entidad_a_modelo(entidad)

    @patch("builtins.print")
    def test_guardar_falla_con_rollback(self, mock_print):
        entidad = MagicMock(Reclamo, id_reclamo=None, usuario_creador=MagicMock(nombre_usuario="user"))
        self.mock_query.filter_by.return_value.first.return_value = MagicMock(id=1)
        self.mock_session.add.side_effect = Exception("DB Constraint Error")
        with self.assertRaisesRegex(Exception, "DB Constraint Error"):
            self.repo.guardar(entidad)
        self.mock_session.rollback.assert_called_once()

    def test_actualizar_sin_id(self):
        entidad = Reclamo(UsuarioFinal("A", "B", "c@d.com", "user", "estudiante", "p"), "Contenido", "maestranza")
        with self.assertRaisesRegex(ValueError, "debe tener un ID"):
            self.repo.actualizar(entidad)

    def test_eliminar_no_encontrado(self):
        self.mock_session.get.return_value = None
        with self.assertRaisesRegex(ValueError, "no encontrado para eliminar"):
            self.repo.eliminar(99)


if __name__ == "__main__":
    unittest.main()
