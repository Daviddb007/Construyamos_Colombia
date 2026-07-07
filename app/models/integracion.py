from __future__ import annotations

from datetime import datetime, timezone

from app import db


class Webhook(db.Model):
    __tablename__ = 'webhooks'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    evento = db.Column(db.String(50), nullable=False, index=True)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ultimo_envio = db.Column(db.DateTime, nullable=True)
    ultimo_estado = db.Column(db.Integer, nullable=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nombre': self.nombre,
            'url': self.url,
            'evento': self.evento,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def activos_por_evento(cls, evento: str):
        return cls.query.filter_by(evento=evento, activo=True).all()
