"""
Modelos de participación ciudadana y clasificación SRIE.

Participacion: registro completo de una participación.
ProblemaReal: catálogo de problemas cotidianos (8 del prototipo).
ClasificacionSRIE: resultado del motor de clasificación.

Optimización: índices compuestos para queries frecuentes del admin y dashboard.
"""
from __future__ import annotations

from datetime import datetime

from app import db


# Tabla asociativa Participacion ↔ Pilar (para búsquedas rápidas)
participacion_pilares = db.Table(
    "participacion_pilares",
    db.Column("participacion_id", db.Integer, db.ForeignKey("participaciones.id"), primary_key=True),
    db.Column("pilar_id", db.Integer, db.ForeignKey("pilares.id"), primary_key=True),
    db.Index("idx_part_pilar_participacion", "participacion_id"),
    db.Index("idx_part_pilar_pilar", "pilar_id"),
)


class ProblemaReal(db.Model):
    """Catálogo de problemas cotidianos (lenguaje ciudadano)."""

    __tablename__ = "problemas_reales"
    __table_args__ = (
        db.Index("idx_problema_activo_orden", "activo", "orden"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    icono = db.Column(db.String(50), nullable=False)
    orden = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    participaciones = db.relationship(
        "Participacion", backref="problema_real", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<ProblemaReal {self.nombre}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "icono": self.icono,
            "orden": self.orden,
        }


class Participacion(db.Model):
    """Participación ciudadana completa."""

    __tablename__ = "participaciones"
    __table_args__ = (
        db.Index("idx_part_dept_fecha", "departamento", "created_at"),
        db.Index("idx_part_problema_fecha", "problema_real_id", "created_at"),
        db.Index("idx_part_fecha_desc", "created_at"),
        db.Index("idx_part_municipio", "municipio"),
    )

    id = db.Column(db.Integer, primary_key=True)

    # Ubicación
    departamento = db.Column(db.String(100), nullable=False, index=True)
    municipio = db.Column(db.String(100), nullable=False)
    zona = db.Column(db.String(20), nullable=False)  # urbana | rural

    # Problema
    problema_real_id = db.Column(
        db.Integer, db.ForeignKey("problemas_reales.id"), nullable=False, index=True
    )

    # Texto libre
    justificacion = db.Column(db.Text, nullable=False)
    propuesta = db.Column(db.Text, nullable=False)

    # Gobernanza
    responsable = db.Column(
        db.String(50), nullable=False
    )  # gobierno_nacional | gobernacion | alcaldia | empresa_privada | academia | comunidad
    beneficiario = db.Column(
        db.String(50), nullable=False
    )  # ninos | jovenes | campesinos | empresarios | adultos_mayores | todos

    # Seguridad y auditoría
    ip_hash = db.Column(db.String(64), nullable=True)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # Relaciones
    clasificaciones = db.relationship(
        "ClasificacionSRIE",
        backref="participacion",
        order_by="ClasificacionSRIE.confianza.desc()",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # Pilares asociados (M:N para búsquedas rápidas)
    pilares = db.relationship(
        "Pilar",
        secondary=participacion_pilares,
        backref="participaciones",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Participacion {self.id} - {self.departamento}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "departamento": self.departamento,
            "municipio": self.municipio,
            "zona": self.zona,
            "problema_real": self.problema_real.to_dict() if self.problema_real else None,
            "justificacion": self.justificacion,
            "propuesta": self.propuesta,
            "responsable": self.responsable,
            "beneficiario": self.beneficiario,
            "clasificaciones": [c.to_dict() for c in self.clasificaciones],
            "created_at": self.created_at.isoformat(),
        }

    def to_admin_dict(self) -> dict:
        data = self.to_dict()
        data["ip_hash"] = self.ip_hash
        return data

    def to_recent_dict(self) -> dict:
        return {
            "id": self.id,
            "departamento": self.departamento,
            "problema": self.problema_real.nombre if self.problema_real else None,
            "propuesta": self.propuesta[:200] + "..." if len(self.propuesta) > 200 else self.propuesta,
            "pilar": self.clasificaciones[0].pilar.nombre if self.clasificaciones else None,
            "confianza": self.clasificaciones[0].confianza if self.clasificaciones else None,
            "created_at": self.created_at.isoformat(),
        }


class ClasificacionSRIE(db.Model):
    """Resultado del motor de clasificación SRIE para una participación.

    Una misma participación puede tener varias filas (top-N clasificaciones)
    ordenadas por confianza descendente.
    """

    __tablename__ = "clasificaciones_srie"
    __table_args__ = (
        db.Index("idx_clasif_pilar_confianza", "pilar_id", "confianza"),
        db.Index("idx_clasif_confianza", "confianza"),
    )

    id = db.Column(db.Integer, primary_key=True)
    participacion_id = db.Column(
        db.Integer, db.ForeignKey("participaciones.id"), nullable=False, index=True
    )
    pilar_id = db.Column(db.Integer, db.ForeignKey("pilares.id"), nullable=False)
    linea_id = db.Column(
        db.Integer, db.ForeignKey("lineas_estrategicas.id"), nullable=True
    )
    componente_id = db.Column(
        db.Integer, db.ForeignKey("componentes.id"), nullable=True
    )
    objetivo_id = db.Column(
        db.Integer, db.ForeignKey("objetivos.id"), nullable=True
    )
    confianza = db.Column(db.Float, nullable=False)  # 0.0 - 1.0
    modelo_usado = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    pilar = db.relationship("Pilar", lazy="joined")
    linea = db.relationship("LineaEstrategica", lazy="joined")
    componente = db.relationship("Componente", lazy="joined")
    objetivo = db.relationship("Objetivo", lazy="joined")

    def __repr__(self) -> str:
        return f"<ClasificacionSRIE pilar={self.pilar_id} confianza={self.confianza}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "pilar": self.pilar.to_dict() if self.pilar else None,
            "linea": self.linea.to_dict() if self.linea else None,
            "componente": self.componente.to_dict() if self.componente else None,
            "objetivo": self.objetivo.to_dict() if self.objetivo else None,
            "confianza": round(self.confianza, 2),
            "modelo_usado": self.modelo_usado,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
