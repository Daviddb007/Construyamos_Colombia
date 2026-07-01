"""Orquestador principal del motor SRIE.

Coordina el matching, cálculo de confianza y generación de explicaciones.
"""
from __future__ import annotations

from app import db
from app.models.plan import Pilar
from app.models.participacion import ClasificacionSRIE
from app.services.srie.matcher import buscar_pilar_por_problema
from app.services.srie.confidence import calcular_confianza
from app.services.srie.explanation import generar_explicacion


def clasificar_participacion(participacion, plan_id: int = 1) -> list[ClasificacionSRIE]:
    """Clasifica una participación contra el plan estratégico activo.

    Retorna una lista de ClasificacionSRIE ordenada por confianza descendente.
    """
    # 1. Buscar pilar principal por problema real
    pilar_principal = buscar_pilar_por_problema(participacion.problema_real.nombre)

    # 2. Calcular confianza
    confianza = calcular_confianza(
        problema_nombre=participacion.problema_real.nombre,
        justificacion=participacion.justificacion,
        propuesta=participacion.propuesta,
        pilar=pilar_principal,
    )

    # 3. Generar explicación
    explicacion = generar_explicacion(
        problema_nombre=participacion.problema_real.nombre,
        pilar=pilar_principal,
        confianza=confianza,
    )

    # 4. Crear registro de clasificación
    clasificacion = ClasificacionSRIE(
        participacion_id=participacion.id,
        pilar_id=pilar_principal.id if pilar_principal else None,
        confianza=confianza,
        modelo_usado="keyword_match",
    )

    db.session.add(clasificacion)
    db.session.flush()

    return clasificacion, explicacion
