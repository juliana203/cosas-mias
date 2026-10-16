"""
main.py

Punto de entrada único de la aplicación: levanta Flask, arma el sistema (repositorios + SubSubsistemaGestionReclamos), 
siembra los datos iniciales desde data/*.txt si todavía no existen, y expone todas las rutas. 
Reemplaza a los antiguos server.py + inicializar_db.py.
"""

import os

from flask import render_template, request, redirect, url_for, session, flash, send_from_directory

from modules.config_db import crear_sesion
from modules.repositorio_concreto import RepositorioUsuariosSQLAlchemy, RepositorioReclamosSQLAlchemy
from modules.sistema import SubSubsistemaGestionReclamos, DEPARTAMENTOS_VALIDOS
from modules.usuarios import JefeDepartamento, SecretarioTecnico, Departamento
from modules.excepciones import (
    AppError, EmailYaRegistradoError, NombreUsuarioYaExisteError,
    ClaustroInvalidoError, UsuarioNoEncontradoError, ReclamoNoEncontradoError,
)
from modules.config import app, login_manager
from modules.formularios import FormRegistro, FormLogin, FormCrearReclamo, FormEditarEstado, FormDerivarReclamo
from modules.gestor_login import GestorDeLogin
from modules.estadisticas import Analitica
from modules.graficas import Graficas
from modules.informes import Informes, ReporteHTML, ReportePDF

RUTA_DATA = os.path.join(os.path.dirname(__file__), "data")

# Armado del sistema
# Una única sesión de SQLAlchemy compartida por ambos repositorios (evita inconsistencias entre sesiones distintas al resolver el creador de un reclamo)

_sesion = crear_sesion()
repo_usuarios = RepositorioUsuariosSQLAlchemy(_sesion)
repo_reclamos = RepositorioReclamosSQLAlchemy(_sesion)
sistema = SubSubsistemaGestionReclamos(repo_usuarios, repo_reclamos)
graficas = Graficas()

gestor_login = GestorDeLogin(login_manager, repo_usuarios)

@app.context_processor
def inject_gestor_login():
    """Inyecta 'gestor_login' en el contexto de todas las plantillas (usado en base.html)."""
    return dict(gestor_login=gestor_login)


@app.template_filter("estado_slug")
def estado_slug(valor: str) -> str:
    """Convierte un valor de estado ('en proceso', 'inválido') en un slug apto para clases CSS."""
    return valor.replace(" ", "_").replace("í", "i")

# Inicialización de datos desde los .txt

def inicializar_datos():
    print("Inicializando datos base")

    # Personal (jefes de departamento y secretaría técnica)
    ruta_personal = os.path.join(RUTA_DATA, "personal_iniciales.txt")
    if os.path.exists(ruta_personal):
        with open(ruta_personal, encoding="utf-8") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                try:
                    rol, nombre, apellido, email, nombre_usuario, contrasena, nombre_depto = linea.split(";")
                except ValueError:
                    print(f"[personal_iniciales.txt:{numero_linea}] línea mal formada, se omite.")
                    continue

                if repo_usuarios.obtener_por_filtro(nombre_usuario=nombre_usuario):
                    continue  # ya existe (re-arranque de la app)

                try:
                    if rol == "jefe_departamento":
                        departamento = Departamento(nombre=nombre_depto.strip())
                        nuevo_personal = JefeDepartamento(nombre, apellido, email, nombre_usuario,
                                                           contrasena, departamento)
                    elif rol == "secretario_tecnico":
                        nuevo_personal = SecretarioTecnico(nombre, apellido, email, nombre_usuario, contrasena)
                    else:
                        print(f"[personal_iniciales.txt:{numero_linea}] rol '{rol}' desconocido, se omite.")
                        continue
                    repo_usuarios.guardar(nuevo_personal)
                    print(f"  > Creado: {rol} '{nombre_usuario}'")
                except AppError as e:
                    print(f"[personal_iniciales.txt:{numero_linea}] no se pudo cargar: {e}")

    # Usuarios finales iniciales
    ruta_usuarios = os.path.join(RUTA_DATA, "usuarios_iniciales.txt")
    if os.path.exists(ruta_usuarios):
        with open(ruta_usuarios, encoding="utf-8") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                try:
                    nombre, apellido, email, nombre_usuario, claustro, contrasena = linea.split(";")
                except ValueError:
                    print(f"[usuarios_iniciales.txt:{numero_linea}] línea mal formada, se omite.")
                    continue
                if repo_usuarios.obtener_por_filtro(nombre_usuario=nombre_usuario):
                    continue
                try:
                    sistema.registrar_usuario(nombre, apellido, email, nombre_usuario, claustro, contrasena)
                    print(f"  > Creado: usuario final '{nombre_usuario}'")
                except AppError as e:
                    print(f"[usuarios_iniciales.txt:{numero_linea}] no se pudo crear: {e}")

    # Reclamos iniciales (se clasifican automáticamente al crearse)
    ruta_reclamos = os.path.join(RUTA_DATA, "reclamos_iniciales.txt")
    if os.path.exists(ruta_reclamos):
        with open(ruta_reclamos, encoding="utf-8") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                try:
                    nombre_usuario, contenido = linea.split(";", 1)
                except ValueError:
                    print(f"[reclamos_iniciales.txt:{numero_linea}] línea mal formada, se omite.")
                    continue

                usuario_creador = repo_usuarios.obtener_por_filtro(nombre_usuario=nombre_usuario.strip())
                if not usuario_creador:
                    print(f"[reclamos_iniciales.txt:{numero_linea}] usuario '{nombre_usuario}' inexistente, se omite.")
                    continue
                if repo_reclamos.obtener_por_filtro(contenido=contenido.strip()):
                    continue  # ya existe (re-arranque de la app)

                try:
                    sistema.crear_reclamo(usuario_creador, contenido.strip())
                    print(f"  > Creado: reclamo de '{nombre_usuario}': {contenido[:30]}...")
                except AppError as e:
                    print(f"[reclamos_iniciales.txt:{numero_linea}] no se pudo crear: {e}")

    print("Inicialización de datos completada")


inicializar_datos()

# Rutas públicas

@app.route("/")
def index():
    if gestor_login.usuario_autenticado:
        if gestor_login.usuario_actual.rol == "usuario_final":
            return redirect(url_for("reclamos_pendientes"))
        return redirect(url_for("panel_departamento"))
    return render_template("index.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    form = FormRegistro()

    if form.validate_on_submit():
        try:
            sistema.registrar_usuario(
                nombre=form.nombre.data, apellido=form.apellido.data, email=form.email.data,
                nombre_usuario=form.nombre_usuario.data, claustro=form.claustro.data,
                contrasena=form.password.data,
            )
            flash("Cuenta creada con éxito. Ya podés iniciar sesión.", "success")
            return redirect(url_for("login"))
        except (EmailYaRegistradoError, NombreUsuarioYaExisteError, ClaustroInvalidoError) as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"No se pudo completar el registro: {e}", "danger")

    return render_template("registro.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = FormLogin()

    if form.validate_on_submit():
        try:
            usuario_entidad = sistema.buscar_usuario(form.nombre_usuario.data)
            if not usuario_entidad.verificar_contrasena(form.password.data):
                raise ValueError("Contraseña incorrecta.")

            gestor_login.login(usuario_entidad)
            flash(f"Bienvenido, {usuario_entidad.nombre}!", "success")

            if usuario_entidad.rol == "usuario_final":
                return redirect(url_for("reclamos_pendientes"))
            return redirect(url_for("panel_departamento"))

        except (UsuarioNoEncontradoError, ValueError) as e:
            flash(f"Error al iniciar sesión: {e}", "danger")
        except Exception as e:
            flash(f"Error inesperado: {e}", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@gestor_login.se_requiere_login
def logout():
    gestor_login.logout()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("index"))


# Reclamos (usuario final)

@app.route("/reclamo/nuevo", methods=["GET", "POST"])
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["usuario_final"])
def reclamo_nuevo():
    """Paso 1: clasifica el contenido y busca reclamos similares antes de crear."""
    form = FormCrearReclamo()

    if form.validate_on_submit():
        contenido = form.contenido.data
        similares = sistema.buscar_reclamos_similares(contenido)

        if not similares:
            try:
                nuevo_reclamo = sistema.crear_reclamo(
                    usuario_creador=gestor_login.usuario_actual.entidad, contenido=contenido,
                )
                flash(f"Reclamo #{nuevo_reclamo.id_reclamo} creado y derivado a '{nuevo_reclamo.departamento}'.", "success")
                return redirect(url_for("reclamos_usu"))
            except Exception as e:
                flash(f"Error al crear el reclamo: {e}", "danger")
        else:
            session["reclamo_temporal"] = contenido
            return render_template("reclamo_similares.html", similares=similares, contenido_nuevo=contenido)

    return render_template("reclamo_nuevo.html", form=form)


@app.route("/reclamo/crear_de_todos_modos", methods=["POST"])
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["usuario_final"])
def reclamo_crear_de_todos_modos():
    """Ninguno de los similares mostrados correspondía: crear el reclamo igual."""
    contenido = session.pop("reclamo_temporal", None)
    if not contenido:
        flash("No hay un reclamo pendiente de confirmar.", "danger")
        return redirect(url_for("reclamo_nuevo"))

    try:
        nuevo_reclamo = sistema.crear_reclamo(
            usuario_creador=gestor_login.usuario_actual.entidad, contenido=contenido,
        )
        flash(f"Reclamo #{nuevo_reclamo.id_reclamo} creado y derivado a '{nuevo_reclamo.departamento}'.", "success")
    except Exception as e:
        flash(f"No se pudo crear el reclamo: {e}", "danger")

    return redirect(url_for("reclamos_usu"))


@app.route("/reclamo/<int:id_reclamo>/confirmar_adhesion", methods=["POST"])
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["usuario_final"])
def reclamo_confirmar_adhesion(id_reclamo):
    """El usuario eligió adherirse a uno de los reclamos similares en vez de crear uno nuevo."""
    session.pop("reclamo_temporal", None)
    try:
        sistema.adherir_a_reclamo(gestor_login.usuario_actual.entidad, id_reclamo)
        flash(f"Te adheriste al reclamo #{id_reclamo}.", "success")
    except Exception as e:
        flash(f"No se pudo adherir al reclamo: {e}", "danger")

    return redirect(url_for("reclamos_usu"))


@app.route("/reclamos/pendientes")
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["usuario_final"])
def reclamos_pendientes():
    departamento_filtro = request.args.get("departamento") or None

    if departamento_filtro:
        reclamos = sistema.buscar_reclamos_pendientes_por_departamento(departamento_filtro)
    else:
        reclamos = sistema.buscar_reclamos_pendientes_todos()

    departamentos = [Departamento(nombre=d) for d in DEPARTAMENTOS_VALIDOS]

    return render_template(
        "reclamos_pendientes.html", reclamos=reclamos,
        departamentos=departamentos, departamento_filtro=departamento_filtro,
    )


@app.route("/reclamos/<int:id_reclamo>/adherirse", methods=["POST"])
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["usuario_final"])
def reclamo_adherirse(id_reclamo):
    try:
        sistema.adherir_a_reclamo(gestor_login.usuario_actual.entidad, id_reclamo)
        flash("Te adheriste al reclamo.", "success")
    except Exception as e:
        flash(f"No se pudo adherir al reclamo: {e}", "danger")

    return redirect(url_for("reclamos_pendientes"))


@app.route("/reclamos/mios")
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["usuario_final"])
def reclamos_usu():
    reclamos = sistema.listar_reclamos_usuario(gestor_login.usuario_actual.entidad)
    return render_template("reclamos_usu.html", reclamos=reclamos)


# Reclamos (jefe de departamento y secretaría técnica)

def _reclamos_visibles_para(usuario_actual) -> list:
    """Jefe de departamento ve sólo su departamento; secretaría técnica ve todo."""
    if usuario_actual.rol == "jefe_departamento":
        return repo_reclamos.obtener_todos_por_filtro(departamento=usuario_actual.departamento)
    return repo_reclamos.obtener_todos()


@app.route("/panel")
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["jefe_departamento", "secretario_tecnico"])
def panel_departamento():
    reclamos = _reclamos_visibles_para(gestor_login.usuario_actual)
    reclamos.sort(key=lambda r: r.estado)
    return render_template("panel_departamento.html", reclamos=reclamos)


@app.route("/reclamos/<int:id_reclamo>/estado", methods=["GET", "POST"])
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["jefe_departamento", "secretario_tecnico"])
def reclamo_estado(id_reclamo):
    try:
        reclamo = sistema.buscar_reclamo_por_id(id_reclamo)
    except ReclamoNoEncontradoError as e:
        flash(str(e), "danger")
        return redirect(url_for("panel_departamento"))

    usuario_actual = gestor_login.usuario_actual
    if usuario_actual.rol == "jefe_departamento" and reclamo.departamento != usuario_actual.departamento:
        flash("Permiso denegado: no puede editar reclamos de otro departamento.", "danger")
        return redirect(url_for("panel_departamento"))

    form = FormEditarEstado()

    if form.validate_on_submit():
        try:
            nuevo_estado = form.estado.data
            tiempo_res = form.tiempo_resolucion.data

            if nuevo_estado == "en proceso" and not tiempo_res:
                flash("Debe asignar un tiempo de resolución (1-15 días) para el estado 'En Proceso'.", "danger")
            else:
                sistema.cambiar_estado_reclamo(
                    usuario=usuario_actual.entidad, id_reclamo=id_reclamo,
                    nuevo_estado=nuevo_estado, dias_resolucion=tiempo_res if tiempo_res else None,
                )
                flash("Estado actualizado.", "success")
                return redirect(url_for("panel_departamento"))
        except Exception as e:
            flash(f"No se pudo cambiar el estado: {e}", "danger")
    else:
        form.estado.data = reclamo.estado
        form.tiempo_resolucion.data = reclamo.tiempo_resolucion_asignado

    return render_template("reclamo_estado.html", reclamo=reclamo, form=form)


@app.route("/reclamos/<int:id_reclamo>/derivar", methods=["GET", "POST"])
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["secretario_tecnico"])
def reclamo_derivar(id_reclamo):
    try:
        reclamo = sistema.buscar_reclamo_por_id(id_reclamo)
    except ReclamoNoEncontradoError as e:
        flash(str(e), "danger")
        return redirect(url_for("panel_departamento"))

    departamentos = [Departamento(nombre=d) for d in DEPARTAMENTOS_VALIDOS]
    form = FormDerivarReclamo()

    if form.validate_on_submit():
        try:
            nuevo_depto = form.departamento.data
            sistema.derivar_reclamo(
                usuario_secretario=gestor_login.usuario_actual.entidad,
                id_reclamo=id_reclamo, nuevo_departamento=nuevo_depto,
            )
            flash(f"Reclamo #{id_reclamo} derivado a '{nuevo_depto}'.", "success")
            return redirect(url_for("panel_departamento"))
        except Exception as e:
            flash(f"No se pudo derivar el reclamo: {e}", "danger")
    else:
        form.departamento.data = reclamo.departamento

    return render_template("reclamo_derivar.html", reclamo=reclamo, departamentos=departamentos, form=form)


# --- Analítica y reportes ---

@app.route("/analitica")
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["jefe_departamento", "secretario_tecnico"])
def analitica_vista():
    reclamos = _reclamos_visibles_para(gestor_login.usuario_actual)

    if not reclamos:
        return render_template(
            "analitica.html", stats={"total": 0}, stats_mediana=0, stats_palabras=[],
            grafico_tor=None, grafico_tie=None, grafico_pf=None,
        )

    analitica_calc = Analitica(reclamos)
    stats = analitica_calc.calcular_porcentaje_estado()
    stats_mediana = analitica_calc.calcular_mediana_tiempos_resolucion()
    stats_palabras = analitica_calc.calcular_palabras_frecuentes(15)

    return render_template(
        "analitica.html", stats=stats, stats_mediana=stats_mediana, stats_palabras=stats_palabras,
        grafico_tor=graficas.generar_grafica_tor(stats),
        grafico_tie=graficas.generar_grafica_tiem(stats_mediana),
        grafico_pf=graficas.generar_grafica_pf(stats_palabras),
    )


@app.route("/analitica/reporte/<tipo>")
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["jefe_departamento", "secretario_tecnico"])
def analitica_reporte(tipo):
    usuario_actual = gestor_login.usuario_actual
    departamento_titulo = "Todos los Departamentos" if usuario_actual.rol == "secretario_tecnico" else usuario_actual.departamento
    reclamos = _reclamos_visibles_para(usuario_actual)

    stats = {"total": 0}
    stats_mediana = 0
    graficos = None
    if reclamos:
        analitica_calc = Analitica(reclamos)
        stats = analitica_calc.calcular_porcentaje_estado()
        stats_mediana = analitica_calc.calcular_mediana_tiempos_resolucion()
        stats_palabras = analitica_calc.calcular_palabras_frecuentes(15)
        graficos = {
            "tor": graficas.generar_grafica_tor(stats),
            "tie": graficas.generar_grafica_tiem(stats_mediana),
            "pf": graficas.generar_grafica_pf(stats_palabras),
        }

    estadisticas_completas = {**stats, "mediana_tiempos": stats_mediana}

    if tipo.lower() == "html":
        estrategia = ReporteHTML()
    elif tipo.lower() == "pdf":
        estrategia = ReportePDF()
    else:
        flash("Formato de reporte no válido.", "danger")
        return redirect(url_for("analitica_vista"))

    informes = Informes(estrategia)
    ruta_archivo = informes.generar_reporte(
        lista_reclamos=reclamos, estadisticas=estadisticas_completas, departamento=departamento_titulo,
        graficos=graficos,
    )

    directorio = os.path.abspath("reportes")
    nombre_archivo = os.path.basename(ruta_archivo)
    return send_from_directory(directory=directorio, path=nombre_archivo, as_attachment=True)


@app.route("/ayuda")
@gestor_login.se_requiere_login
@gestor_login.rol_requerido(roles_permitidos=["jefe_departamento", "secretario_tecnico"])
def ayuda():
    return render_template("ayuda.html")


# --- Punto de entrada ---
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)