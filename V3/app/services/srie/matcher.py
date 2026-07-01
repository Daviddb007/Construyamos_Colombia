"""Matching semántico: problema real → pilar del plan estratégico.

Usa mapping directo (keywords) para clasificación inicial.
"""
from __future__ import annotations

from app.models.plan import Pilar
from app.seed.seed_plan import PROBLEMA_PILAR_MAP


def buscar_pilar_por_problema(nombre_problema: str) -> Pilar | None:
    """Busca el pilar correspondiente a un problema real.

    Usa el mapping PROBLEMA_PILAR_MAP definido en el seed.
    Retorna None si no hay mapping (caso "Otro").
    """
    pilar_orden = PROBLEMA_PILAR_MAP.get(nombre_problema)
    if pilar_orden is None:
        return None

    pilar = Pilar.query.filter_by(orden=pilar_orden, activo=True).first()
    return pilar
