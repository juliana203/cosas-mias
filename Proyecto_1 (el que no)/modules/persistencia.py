"""
persistencia.py

Agrupa la Base declarativa de SQLAlchemy y las tres tablas (modelos) del
sistema. Esta es la ÚNICA parte del proyecto que conoce SQLAlchemy
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from flask_login import UserMixin

Base = declarative_base()


reclamo_adherentes = Table(
    "reclamo_adherentes",
    Base.metadata,
    Column("id_reclamo", Integer, ForeignKey("reclamos.id"), primary_key=True),
    Column("id_usuario", Integer, ForeignKey("usuarios.id"), primary_key=True),
)

class ModeloDepartamento(Base):
    __tablename__ = "departamentos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), unique=True, nullable=False)


class ModeloUsuario(Base, UserMixin):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), nullable=False)
    apellido = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    nombreUsuario = Column(String(80), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    claustro = Column(String(20), nullable=True)          # solo aplica a UsuarioFinal
    rol = Column(String(30), nullable=False)               # 'usuario_final' | 'jefe_departamento' | 'secretario_tecnico'
    departamentoAsignado = Column(Integer, ForeignKey("departamentos.id"), nullable=True)

    departamento = relationship("ModeloDepartamento", foreign_keys=[departamentoAsignado])
    reclamos_creados = relationship(
        "ModeloReclamo", back_populates="creador",
        foreign_keys="ModeloReclamo.idUsuarioCreador",
    )
    reclamos_adheridos = relationship(
        "ModeloReclamo", secondary=reclamo_adherentes, back_populates="adherentes",
    )

    def get_id(self) -> str:  # requerido por Flask-Login
        return str(self.id)


class ModeloReclamo(Base):
    __tablename__ = "reclamos"

    id = Column(Integer, primary_key=True)
    contenido = Column(String(2000), nullable=False)
    departamento = Column(Integer, ForeignKey("departamentos.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    estado = Column(String(20), nullable=False, default="pendiente")
    tiempoResolucionAsignado = Column(Integer, nullable=True)
    idUsuarioCreador = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    rutaImagen = Column(String(500), nullable=True)  # foto adjunta (opcional)

    creador = relationship(
        "ModeloUsuario", back_populates="reclamos_creados",
        foreign_keys=[idUsuarioCreador],
    )
    depto = relationship("ModeloDepartamento", foreign_keys=[departamento])
    adherentes = relationship(
        "ModeloUsuario", secondary=reclamo_adherentes, back_populates="reclamos_adheridos",
    )
