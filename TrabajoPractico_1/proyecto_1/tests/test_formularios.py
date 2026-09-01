import unittest
from werkzeug.datastructures import MultiDict

from modules.formularios import FormRegistro, FormEditarEstado, FormCrearReclamo


def simular_form(form_class, data):
    form = form_class(formdata=MultiDict(data))
    form.validate()
    return form


class TestFormularios(unittest.TestCase):
    def setUp(self):
        from modules.config import app
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.config.update({"WTF_CSRF_ENABLED": False, "TESTING": True})

    def tearDown(self):
        self.app_context.pop()

    def test_form_registro_contrasenas_no_coinciden(self):
        data = {
            "nombre": "A", "apellido": "B", "email": "a@b.com", "nombre_usuario": "user",
            "claustro": "estudiante", "password": "pass1", "confirmacion": "pass2", "submit": True,
        }
        form = simular_form(FormRegistro, data)
        self.assertFalse(form.validate())
        self.assertIn("Las contraseñas deben coincidir", form.confirmacion.errors[0])

    def test_form_registro_email_invalido(self):
        data = {
            "nombre": "A", "apellido": "B", "email": "no_es_un_email", "nombre_usuario": "user",
            "claustro": "estudiante", "password": "pass1", "confirmacion": "pass1", "submit": True,
        }
        form = simular_form(FormRegistro, data)
        self.assertFalse(form.validate())
        self.assertTrue(len(form.email.errors) > 0)

    def test_form_registro_ok(self):
        data = {
            "nombre": "A", "apellido": "B", "email": "a@b.com", "nombre_usuario": "user",
            "claustro": "PAyS", "password": "pass1", "confirmacion": "pass1", "submit": True,
        }
        form = simular_form(FormRegistro, data)
        self.assertTrue(form.validate())

    def test_form_crear_reclamo_longitud_invalida(self):
        data = {"contenido": "corto", "submit": True}
        form = simular_form(FormCrearReclamo, data)
        self.assertFalse(form.validate())

    def test_form_crear_reclamo_longitud_valida(self):
        data = {"contenido": "Este es un contenido de prueba con longitud suficiente.", "submit": True}
        form = simular_form(FormCrearReclamo, data)
        self.assertTrue(form.validate())

    def test_form_editar_estado_tiempo_resolucion_fuera_de_rango(self):
        data = {"estado": "en proceso", "tiempo_resolucion": 0, "submit": True}
        form = simular_form(FormEditarEstado, data)
        self.assertFalse(form.validate())
        self.assertTrue(len(form.tiempo_resolucion.errors) > 0)

    def test_form_editar_estado_tiempo_resolucion_opcional(self):
        data = {"estado": "resuelto", "tiempo_resolucion": "", "submit": True}
        form = simular_form(FormEditarEstado, data)
        self.assertTrue(form.validate())


if __name__ == "__main__":
    unittest.main()
