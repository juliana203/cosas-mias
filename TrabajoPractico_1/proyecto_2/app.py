"""
app.py

Proyecto de prueba, chico a propósito: solo sirve para validar que el
despliegue en RunxBuild funciona de punta a punta (Postgres + gunicorn).
No tiene login, ni validaciones finas, ni nada del TP3 real.
"""

import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Conexión a la base (mismo truco que en config_db.py del otro proyecto) ---

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine("sqlite:///torneo.db")

Session = sessionmaker(bind=engine)
Base = declarative_base()


# --- Modelos ---

class Equipo(Base):
    __tablename__ = "equipos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)


class Resultado(Base):
    __tablename__ = "resultados"
    id = Column(Integer, primary_key=True)
    equipo_nombre = Column(String(100), nullable=False)
    disciplina = Column(String(100), nullable=False)
    puntos = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.now)


Base.metadata.create_all(engine)

app = Flask(__name__)
app.config["SECRET_KEY"] = "solo-para-probar-el-despliegue"


# --- Rutas ---

@app.route("/")
def inicio():
    return redirect(url_for("ranking"))


@app.route("/grupo")
def grupo():
    session = Session()
    equipos = session.query(Equipo).order_by(Equipo.nombre).all()
    session.close()
    return render_template("grupo.html", equipos=equipos)


@app.route("/resultados/nuevo", methods=["GET", "POST"])
def resultado_nuevo():
    session = Session()

    if request.method == "POST":
        equipo_nombre = request.form.get("equipo", "").strip()
        disciplina = request.form.get("disciplina", "").strip()
        puntos = request.form.get("puntos", "").strip()

        if equipo_nombre and disciplina and puntos.lstrip("-").isdigit():
            # Si el equipo no existe todavía, se crea solo (sin formulario aparte).
            existente = session.query(Equipo).filter_by(nombre=equipo_nombre).first()
            if not existente:
                session.add(Equipo(nombre=equipo_nombre))

            session.add(Resultado(equipo_nombre=equipo_nombre, disciplina=disciplina, puntos=int(puntos)))
            session.commit()
            session.close()
            return redirect(url_for("ranking"))

    equipos = session.query(Equipo).order_by(Equipo.nombre).all()
    session.close()
    return render_template("resultado_nuevo.html", equipos=equipos)


@app.route("/ranking")
def ranking():
    session = Session()
    filas = (
        session.query(Resultado.equipo_nombre, func.sum(Resultado.puntos).label("total"))
        .group_by(Resultado.equipo_nombre)
        .order_by(func.sum(Resultado.puntos).desc())
        .all()
    )
    session.close()
    return render_template("ranking.html", filas=filas)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
