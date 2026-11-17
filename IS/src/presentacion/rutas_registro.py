"""Capa de presentación: Rutas de registro (Flask). Reciben el pedido, llaman a un servicio y arman la respuesta.

No contienen reglas de negocio: solo pasan los datos del formulario al Ejecutor de registro y muestran
lo que responde (confirmación, coincidencias o errores traducidos por Gestión de excepciones).
"""
from __future__ import annotations

import base64
from datetime import date

from flask import Flask, render_template, request

from ..dominio.entidades import Parametro
from ..dominio.registro_tecnicas import RegistroTecnicas
from ..dominio.solicitud import DatosRegistro
from ..servicios.ejecutor_registro import EjecutorRegistro
from ..servicios.servicio_consulta import ServicioConsulta
from ..transversal.gestion_excepciones import ErrorPrevisto, PideConfirmacion, traducir

CANTIDAD_EXTRAS = 3


def _leer_datos(form, archivos) -> DatosRegistro:
    """Transcribe lo que llegó del formulario a DatosRegistro, sin validar nada."""
    tipo = form.get("tipo", "")
    valores = {k[2:]: v for k, v in form.items() if k.startswith("v_")}
    extras = []
    for i in range(1, CANTIDAD_EXTRAS + 1):
        nombre, valor = form.get(f"extra_nombre_{i}", "").strip(), form.get(f"extra_valor_{i}", "").strip()
        if nombre or valor:
            extras.append(Parametro(nombre, valor, form.get(f"extra_unidad_{i}", "").strip() or None))
    try:
        fecha = date.fromisoformat(form.get("fecha_realizacion", ""))
    except ValueError:
        fecha = None
    pdb = None
    if "pdb_b64" in form:  # re-envío con confirmación: el PDB viaja en el formulario
        pdb = base64.b64decode(form["pdb_b64"]) if form["pdb_b64"] else None
    elif archivos.get("pdb") and archivos["pdb"].filename:
        pdb = archivos["pdb"].read()
    return DatosRegistro(
        proyecto_id=form.get("proyecto_id", ""),
        tipo=tipo,
        fecha_realizacion=fecha,
        valores=valores,
        extras=extras,
        hardware=form.get("hardware", ""),
        tiempo_procesamiento=form.get("tiempo_procesamiento", ""),
        objetivo=form.get("objetivo", ""),
        hipotesis=form.get("hipotesis", ""),
        notas=form.get("notas", ""),
        similar_a=form.getlist("similar_a"),
        pdb=pdb,
    )


def crear_app(
    ejecutor: EjecutorRegistro,
    tecnicas: RegistroTecnicas,
    consulta: ServicioConsulta,
    autor: str,
) -> Flask:
    app = Flask(__name__)

    def mostrar_formulario(tipo: str, form=None, mensajes=None):
        tecnica = tecnicas.obtener(tipo)
        return render_template(
            "formulario.html",
            tecnicas=tecnicas.disponibles(),
            tecnica=tecnica,
            proyectos=consulta.proyectos(),
            experimentos=consulta.experimentos(),
            form=form or {},
            mensajes=mensajes or [],
            extras=range(1, CANTIDAD_EXTRAS + 1),
        )

    def registrar(confirmado: bool):
        datos = _leer_datos(request.form, request.files)
        try:
            experimento = ejecutor.registrar(datos, autor, confirmado=confirmado)
        except PideConfirmacion as e:
            campos = [(k, v) for k in request.form for v in request.form.getlist(k) if k != "pdb_b64"]
            pdb_b64 = base64.b64encode(datos.pdb).decode() if datos.pdb else ""
            return render_template(
                "coincidencias.html",
                coincidencias=e.coincidencias,
                campos=campos,
                pdb_b64=pdb_b64,
                clave=tecnicas.obtener(datos.tipo).clave_coincidencia(),
            )
        except ErrorPrevisto as e:
            respuesta = traducir(e)
            return mostrar_formulario(datos.tipo or "docking", request.form, respuesta["mensajes"]), 400
        return render_template("resultado.html", experimento=experimento)

    @app.get("/")
    @app.get("/registro")
    def formulario():
        return mostrar_formulario(request.args.get("tipo") or tecnicas.disponibles()[0].tipo)

    @app.post("/registro")
    def registrar_experimento():
        return registrar(confirmado=False)

    @app.post("/registro/confirmar")
    def continuar_pese_a_coincidencia():
        return registrar(confirmado=True)

    @app.post("/registro/cancelar")
    def cancelar_registro():
        return render_template("cancelado.html")

    return app
