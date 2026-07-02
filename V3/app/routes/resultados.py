"""Blueprint de resultados públicos.

Dashboard con estadísticas agregadas y tabla de participaciones recientes.
"""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify

from app import db, cache
from app.models.participacion import Participacion, ClasificacionSRIE, ProblemaReal
from app.models.plan import Pilar

resultados_bp = Blueprint("resultados", __name__)


@resultados_bp.route("/resultados")
@cache.cached(timeout=60)
def resultados():
    total = Participacion.query.count()
    municipios = db.session.query(db.func.count(db.distinct(Participacion.municipio))).scalar() or 0
    pilares = db.session.query(db.func.count(db.distinct(ClasificacionSRIE.pilar_id))).scalar() or 0
    problemas = db.session.query(db.func.count(db.distinct(ProblemaReal.id))).scalar() or 0

    stats = {
        "total": total,
        "municipios": municipios,
        "pilares": pilares,
        "problemas": problemas,
    }
    return render_template("resultados.html", stats=stats)


@resultados_bp.route("/api/estadisticas")
@cache.cached(timeout=60)
def api_estadisticas():
    total = Participacion.query.count()
    departamentos = (
        db.session.query(
            Participacion.departamento,
            db.func.count(Participacion.id),
        )
        .group_by(Participacion.departamento)
        .order_by(db.func.count(Participacion.id).desc())
        .all()
    )
    problemas = (
        db.session.query(
            ProblemaReal.nombre,
            db.func.count(Participacion.id),
        )
        .join(ProblemaReal, ProblemaReal.id == Participacion.problema_real_id)
        .group_by(ProblemaReal.nombre)
        .order_by(db.func.count(Participacion.id).desc())
        .all()
    )
    pilares = (
        db.session.query(
            Pilar.nombre,
            db.func.count(ClasificacionSRIE.id),
        )
        .join(Pilar, Pilar.id == ClasificacionSRIE.pilar_id)
        .group_by(Pilar.nombre)
        .order_by(db.func.count(ClasificacionSRIE.id).desc())
        .all()
    )
    return jsonify({
        "total": total,
        "departamentos": [{"nombre": d, "total": c} for d, c in departamentos],
        "problemas": [{"nombre": p, "total": c} for p, c in problemas],
        "pilares": [{"nombre": p, "total": c} for p, c in pilares],
    })


@resultados_bp.route("/api/participaciones")
@cache.cached(timeout=30, query_string=True)
def api_participaciones():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = (
        Participacion.query
        .order_by(Participacion.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return jsonify({
        "participaciones": [p.to_recent_dict() for p in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": page,
    })

