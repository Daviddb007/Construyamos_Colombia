"""
Seed de datos para Construyamos Colombia V3.

Plan: "El Milagro de los 'Nunca' — Primeros Pilares para Reconstruir la Patria Milagro"
Fuente: Plan de gobierno de Abelardo de la Espriella (2026-2030)

18 pilares: 2 fundacionales + 16 temáticos
8 problemas reales (catálogo del formulario)
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date

from app import db
from app.models.plan import Plan, Pilar, LineaEstrategica, Componente, Objetivo
from app.models.participacion import ProblemaReal


# ---------------------------------------------------------------------
# 1. Plan
# ---------------------------------------------------------------------
PLAN_NOMBRE = "El Milagro de los 'Nunca' — Primeros Pilares para Reconstruir la Patria Milagro"

# ---------------------------------------------------------------------
# 2. Pilares (orden = orden de aparición en el documento fuente)
#    tipo: 'fundacional' = pilares introductorios, sin numerar
#          'tematico'    = los 16 "milagros" numerados
# ---------------------------------------------------------------------
PILARES: list[dict] = [
    # Fundacionales (p. 7 y p. 11)
    {"orden": 0, "tipo": "fundacional", "nombre": "Movimiento Popular"},
    {"orden": 1, "tipo": "fundacional", "nombre": "Pilar Democrático: los Defensores de la Patria"},
    # Milagros temáticos numerados 1-16
    {"orden": 2, "tipo": "tematico", "nombre": "El Milagro de Iluminar la Patria"},
    {"orden": 3, "tipo": "tematico", "nombre": "El Milagro de Defender la Patria para Salvarla"},
    {"orden": 4, "tipo": "tematico", "nombre": "El Milagro de la Extrema Coherencia"},
    {"orden": 5, "tipo": "tematico", "nombre": "El Milagro de la Seguridad"},
    {"orden": 6, "tipo": "tematico", "nombre": "El Milagro de Erradicar la Corrupción"},
    {"orden": 7, "tipo": "tematico", "nombre": "El Milagro de Recuperar la Salud"},
    {"orden": 8, "tipo": "tematico", "nombre": "El Milagro del Campo y el Agro"},
    {"orden": 9, "tipo": "tematico", "nombre": "El Milagro de una Patria para las Mujeres"},
    {"orden": 10, "tipo": "tematico", "nombre": "El Milagro Minero-Energético"},
    {"orden": 11, "tipo": "tematico", "nombre": "El Milagro de la Educación"},
    {"orden": 12, "tipo": "tematico", "nombre": "El Milagro de la Cultura"},
    {"orden": 13, "tipo": "tematico", "nombre": "El Milagro de Proteger el Medioambiente"},
    {"orden": 14, "tipo": "tematico", "nombre": "El Milagro del Bienestar Animal Integral"},
    {"orden": 15, "tipo": "tematico", "nombre": "El Milagro de las Megacárceles y los Megacentros"},
    {"orden": 16, "tipo": "tematico", "nombre": "El Milagro de Defender la Constitución de 1991"},
    {"orden": 17, "tipo": "tematico", "nombre": "El Milagro de los Jóvenes"},
]

# Líneas estratégicas confirmadas para el Pilar Democrático (páginas 11-17)
LINEAS_PILAR_DEMOCRATICO: list[str] = [
    "El Patriotismo Constitucional",
    "Un pilar para sostenerse contra la ofensiva constituyente",
    "Contrato de lealtad con la Constitución",
    "No más combinación de todas las formas de lucha",
    "El alcance de nuestra propuesta",
]

# ---------------------------------------------------------------------
# 3. Catálogo de "problemas reales" para el paso 2 del formulario.
#    Lenguaje cotidiano, mapeado 1:1 a un pilar temático.
# ---------------------------------------------------------------------
PROBLEMAS_REALES: list[dict] = [
    {"nombre": "Conseguir empleo", "icono": "briefcase", "orden": 1},
    {"nombre": "Seguridad", "icono": "shield", "orden": 2},
    {"nombre": "Educación", "icono": "school", "orden": 3},
    {"nombre": "Salud", "icono": "heart", "orden": 4},
    {"nombre": "Corrupción", "icono": "scale", "orden": 5},
    {"nombre": "Campo y agro", "icono": "plant-2", "orden": 6},
    {"nombre": "Medioambiente", "icono": "leaf", "orden": 7},
    {"nombre": "Otro", "icono": "dots", "orden": 8},
]

# ---------------------------------------------------------------------
# 4. Mapping problema → pilar (para el motor SRIE)
# ---------------------------------------------------------------------
PROBLEMA_PILAR_MAP: dict[str, int | None] = {
    "Conseguir empleo": 10,  # El Milagro Minero-Energético (generación de industria)
    "Seguridad": 5,  # El Milagro de la Seguridad
    "Educación": 11,  # El Milagro de la Educación
    "Salud": 7,  # El Milagro de Recuperar la Salud
    "Corrupción": 6,  # El Milagro de Erradicar la Corrupción
    "Campo y agro": 8,  # El Milagro del Campo y el Agro
    "Medioambiente": 13,  # El Milagro de Proteger el Medioambiente
    "Otro": None,  # Sin clasificar automáticamente
}


def _slugify(texto: str) -> str:
    """Convierte texto a slug URL-friendly."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^\w\s-]", "", texto).strip().lower()
    return re.sub(r"[\s_-]+", "-", texto)


def seed_plan() -> None:
    """Siembra el plan estratégico con sus 18 pilares.

    Idempotente: si ya existe un plan activo con el mismo nombre, no lo duplica.
    """
    if Plan.query.filter_by(nombre=PLAN_NOMBRE).first():
        print("  El plan ya existe, no se vuelve a sembrar.")
        return

    plan = Plan(
        nombre=PLAN_NOMBRE,
        version="1.0",
        ambito="nacional",
        vigencia_inicio=date(2026, 8, 7),
        vigencia_fin=date(2030, 8, 6),
        activo=True,
    )
    db.session.add(plan)
    db.session.flush()

    pilar_democratico = None

    for p in PILARES:
        pilar = Pilar(
            plan_id=plan.id,
            nombre=p["nombre"],
            slug=_slugify(p["nombre"]),
            tipo=p["tipo"],
            orden=p["orden"],
        )
        db.session.add(pilar)
        db.session.flush()

        if p["nombre"].startswith("Pilar Democrático"):
            pilar_democratico = pilar
            for i, nombre_linea in enumerate(LINEAS_PILAR_DEMOCRATICO):
                db.session.add(
                    LineaEstrategica(pilar_id=pilar.id, nombre=nombre_linea, orden=i)
                )
        else:
            db.session.add(
                LineaEstrategica(
                    pilar_id=pilar.id,
                    nombre=f"Línea general — {p['nombre']}",
                    orden=0,
                    descripcion="Pendiente de desglose en líneas/componentes/objetivos específicos.",
                )
            )

    # Ejemplo de desglose completo hasta Objetivo (Pilar Democrático)
    if pilar_democratico:
        primera_linea = LineaEstrategica.query.filter_by(
            pilar_id=pilar_democratico.id, orden=0
        ).first()
        if primera_linea:
            componente = Componente(
                linea_id=primera_linea.id,
                nombre="Reconocimiento constitucional del vínculo cívico",
            )
            db.session.add(componente)
            db.session.flush()
            db.session.add(
                Objetivo(
                    componente_id=componente.id,
                    nombre="Fortalecer la adhesión ciudadana a la Constitución de 1991",
                    ods="16",
                )
            )

    db.session.commit()
    print(f"  Plan '{plan.nombre}' sembrado con {len(PILARES)} pilares.")


def seed_problemas() -> None:
    """Siembra el catálogo de problemas reales (8 del prototipo).

    Idempotente: si ya existen problemas, no los duplica.
    """
    if ProblemaReal.query.count() > 0:
        print("  Los problemas reales ya existen, no se vuelve a sembrar.")
        return

    for pr in PROBLEMAS_REALES:
        db.session.add(ProblemaReal(**pr, activo=True))

    db.session.commit()
    print(f"  {len(PROBLEMAS_REALES)} problemas reales sembrados.")


def run_all() -> None:
    """Ejecuta todos los seeds en orden. Para usar con 'flask seed'."""
    print("=== Sembrando datos V3 ===")
    seed_plan()
    seed_problemas()
    print("=== Seed completado ===")
