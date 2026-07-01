"""Validación y sanitización de inputs para participaciones.

Valida todos los campos requeridos antes de persistir.
Sanitiza textos libres para prevenir XSS.
"""
from __future__ import annotations

import bleach

from app.errors import ValidationError

# Allowed HTML tags for text fields (none — strip everything)
ALLOWED_TAGS: list[str] = []
ALLOWED_ATTRIBUTES: dict = {}


DEPARTAMENTOS_COL: list[str] = [
    "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá D.C.",
    "Bolívar", "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca",
    "Cesar", "Chocó", "Córdoba", "Cundinamarca", "Guainía", "Guaviare",
    "Huila", "La Guajira", "Magdalena", "Meta", "Nariño",
    "Norte de Santander", "Putumayo", "Quindío", "Risaralda",
    "San Andrés y Providencia", "Santander", "Sucre", "Tolima",
    "Valle del Cauca", "Vaupés", "Vichada",
]

VALID_RANGOS_EDAD: list[str] = [
    "16-18", "19-25", "26-35", "36-45", "46-55", "56-65", "66+",
]

VALID_GENEROS: list[str] = [
    "Masculino", "Femenino", "Otro", "Prefiero no decir",
]

VALID_ZONAS: list[str] = ["urbana", "rural"]

VALID_RESPONSABLES: list[str] = [
    "gobierno_nacional", "gobernacion", "alcaldia",
    "empresa_privada", "academia", "comunidad",
]

VALID_BENEFICIARIOS: list[str] = [
    "ninos", "jovenes", "campesinos", "empresarios",
    "adultos_mayores", "todos",
]


def sanitize_text(text: str) -> str:
    """Sanitiza texto libre eliminando HTML y scripts."""
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES).strip()


def validate_participacion(data: dict) -> dict:
    """Valida y sanitiza datos de participación. Retorna datos sanitizados."""
    _validate_ubicacion(data)
    _validate_problema(data)
    _validate_textos(data)
    _validate_gobernanza(data)

    # Sanitize text fields
    return {
        "departamento": data["departamento"],
        "municipio": sanitize_text(data["municipio"]),
        "zona": data["zona"],
        "problema_real_id": data["problema_real_id"],
        "justificacion": sanitize_text(data["justificacion"]),
        "propuesta": sanitize_text(data["propuesta"]),
        "responsable": data["responsable"],
        "beneficiario": data["beneficiario"],
    }


def _validate_ubicacion(data: dict) -> None:
    departamento = data.get("departamento", "")
    if not departamento:
        raise ValidationError("El departamento es requerido")
    if departamento not in DEPARTAMENTOS_COL:
        raise ValidationError("Departamento inválido")

    municipio = data.get("municipio", "")
    if not municipio or not municipio.strip():
        raise ValidationError("El municipio es requerido")
    if len(municipio) > 100:
        raise ValidationError("El municipio debe tener máximo 100 caracteres")

    zona = data.get("zona", "")
    if not zona:
        raise ValidationError("La zona es requerida")
    if zona not in VALID_ZONAS:
        raise ValidationError("Zona inválida (debe ser 'urbana' o 'rural')")


def _validate_problema(data: dict) -> None:
    problema_real_id = data.get("problema_real_id")
    if not problema_real_id:
        raise ValidationError("Debe seleccionar un problema")


def _validate_textos(data: dict) -> None:
    justificacion = data.get("justificacion", "")
    if not justificacion or not justificacion.strip():
        raise ValidationError("La justificación es requerida")
    if len(justificacion) > 500:
        raise ValidationError("La justificación debe tener máximo 500 caracteres")

    propuesta = data.get("propuesta", "")
    if not propuesta or not propuesta.strip():
        raise ValidationError("La propuesta es requerida")
    if len(propuesta) > 500:
        raise ValidationError("La propuesta debe tener máximo 500 caracteres")


def _validate_gobernanza(data: dict) -> None:
    responsable = data.get("responsable", "")
    if not responsable:
        raise ValidationError("Debe seleccionar quién debería liderar")
    if responsable not in VALID_RESPONSABLES:
        raise ValidationError("Responsable inválido")

    beneficiario = data.get("beneficiario", "")
    if not beneficiario:
        raise ValidationError("Debe seleccionar a quién beneficia")
    if beneficiario not in VALID_BENEFICIARIOS:
        raise ValidationError("Beneficiario inválido")
