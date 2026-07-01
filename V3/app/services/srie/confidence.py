"""Cálculo de confianza para clasificaciones SRIE.

Niveles:
    Alto:   0.80 - 1.00  (clasificación automática)
    Medio:  0.50 - 0.79  (clasificación + revisión sugerida)
    Bajo:   0.20 - 0.49  (clasificación provisional)
    Sin clasificar: 0.00 - 0.19 (cola de revisión manual)
"""
from __future__ import annotations


def calcular_confianza(
    problema_nombre: str,
    justificacion: str,
    propuesta: str,
    pilar,
) -> float:
    """Calcula el nivel de confianza de una clasificación.

    Estrategia actual (keyword matching):
    - Si hay pilar directo (problema → pilar): confianza alta (0.85-0.97)
    - Si es "Otro": confianza 0.0 (requiere revisión manual)

    Futuro: se puede agregar NLP (TF-IDF, embeddings) para refinar.
    """
    if pilar is None:
        return 0.0

    # Confianza base por匹配 directa
    confianza_base = {
        "Conseguir empleo": 0.78,
        "Seguridad": 0.95,
        "Educación": 0.93,
        "Salud": 0.96,
        "Corrupción": 0.94,
        "Campo y agro": 0.97,
        "Medioambiente": 0.92,
    }

    confianza = confianza_base.get(problema_nombre, 0.85)

    # Bonus por texto sustancial
    texto_total = f"{justificacion} {propuesta}"
    if len(texto_total) > 200:
        confianza = min(confianza + 0.02, 1.0)

    return round(confianza, 2)
