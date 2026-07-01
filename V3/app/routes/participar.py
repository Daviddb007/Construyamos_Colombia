"""Blueprint de participación ciudadana.

Formulario conversacional 5 pasos + POST /api/enviar + SRIE classification.
"""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app import db, limiter
from app.decorators import get_client_ip, hash_ip
from app.errors import ValidationError, DatabaseError
from app.models.participacion import Participacion, ProblemaReal, ClasificacionSRIE
from app.services.validation import validate_participacion
from app.services.srie.classifier import clasificar_participacion

participar_bp = Blueprint("participar", __name__)


@participar_bp.route("/participar")
def participar():
    return render_template("participar.html")


@participar_bp.route("/api/problemas")
def api_problemas():
    problemas = ProblemaReal.query.filter_by(activo=True).order_by(ProblemaReal.orden).all()
    return jsonify([p.to_dict() for p in problemas])


@participar_bp.route("/api/enviar", methods=["POST"])
@limiter.limit("5 per minute;20 per hour")
def api_enviar():
    data = request.get_json(silent=True)
    if not data:
        raise ValidationError("Se esperaba JSON")

    # Validate and sanitize
    sanitized = validate_participacion(data)

    ip = get_client_ip()
    ip_h = hash_ip(ip)

    participacion = Participacion(
        departamento=sanitized["departamento"],
        municipio=sanitized["municipio"],
        zona=sanitized["zona"],
        problema_real_id=sanitized["problema_real_id"],
        justificacion=sanitized["justificacion"],
        propuesta=sanitized["propuesta"],
        responsable=sanitized["responsable"],
        beneficiario=sanitized["beneficiario"],
        ip_hash=ip_h,
    )

    try:
        db.session.add(participacion)
        db.session.flush()
    except Exception as e:
        db.session.rollback()
        raise DatabaseError("Error al guardar la participación")

    try:
        clasificacion, explicacion = clasificar_participacion(participacion)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise DatabaseError("Error al clasificar la participación")

    return jsonify({
        "success": True,
        "id": participacion.id,
        "clasificacion": {
            "pilar": clasificacion.pilar.to_dict() if clasificacion.pilar else None,
            "confianza": clasificacion.confianza,
            "explicacion": explicacion,
        },
    }), 201
