"""Generación de explicaciones para el ciudadano.

Crea textos claros que explican por qué su propuesta fue clasificada
en un pilar específico.
"""
from __future__ import annotations


def generar_explicacion(
    problema_nombre: str,
    pilar,
    confianza: float,
) -> str:
    """Genera una explicación legible para el ciudadano.

    Retorna un string en español que explica la clasificación.
    """
    if pilar is None:
        return (
            "No fue posible clasificar tu propuesta automáticamente. "
            "Un moderador la revisará manualmente."
        )

    if confianza >= 0.85:
        return (
            f"Tu propuesta sobre '{problema_nombre}' se relaciona directamente "
            f"con el pilar \"{pilar.nombre}\"."
        )

    if confianza >= 0.50:
        return (
            f"Tu propuesta sobre '{problema_nombre}' se relaciona parcialmente "
            f"con el pilar \"{pilar.nombre}\". Un moderador podría ajustar "
            f"esta clasificación."
        )

    return (
        f"Tu propuesta sobre '{problema_nombre}' fue clasificada provisionalmente "
        f"en el pilar \"{pilar.nombre}\". La confianza es baja y podría "
        f"reclasificarse."
    )
