from src.transversal.gestion_excepciones import (ErrorAlmacenamiento, ErrorPrevisto, ErrorValidacion,
                                                  PideConfirmacion, traducir)


def test_traduce_errores_de_validacion():
    r = traducir(ErrorValidacion(["a", "b"]))
    assert r == {"tipo": "validacion", "mensajes": ["a", "b"]}


def test_traduce_coincidencias():
    assert traducir(PideConfirmacion([object()]))["tipo"] == "coincidencias"


def test_traduce_falla_de_almacenamiento_con_mensaje_para_el_usuario():
    r = traducir(ErrorAlmacenamiento("disco"))
    assert r["tipo"] == "almacenamiento" and "no quedó nada guardado" in r["mensajes"][0]


def test_traduce_un_error_previsto_generico():
    assert traducir(ErrorPrevisto("x"))["tipo"] == "desconocido"
