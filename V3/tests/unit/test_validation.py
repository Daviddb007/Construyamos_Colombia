"""Tests unitarios para validación de inputs y motor SRIE."""
import pytest

from app.errors import ValidationError
from app.services.validation import validate_participacion, sanitize_text


class TestSanitizeText:

    def test_strips_html_tags(self):
        result = sanitize_text("<script>alert('x')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

    def test_strips_nested_tags(self):
        result = sanitize_text("<b><i>Bold italic</i></b>")
        assert "<b>" not in result
        assert "Bold italic" in result

    def test_preserves_plain_text(self):
        result = sanitize_text("This is plain text")
        assert result == "This is plain text"

    def test_strips_event_handlers(self):
        result = sanitize_text('<div onmouseover="alert(1)">Text</div>')
        assert "onmouseover" not in result

    def test_strips_images(self):
        result = sanitize_text('<img src="x" onerror="alert(1)">')
        assert "<img" not in result


class TestValidateUbicacion:

    def test_requiere_departamento(self):
        data = {"municipio": "Bogotá", "zona": "urbana", "problema_real_id": 1,
                "justificacion": "Test", "propuesta": "Test", "responsable": "alcaldia",
                "beneficiario": "todos"}
        with pytest.raises(ValidationError, match="departamento es requerido"):
            validate_participacion(data)

    def test_departamento_invalido(self):
        data = {"departamento": "Atlantis", "municipio": "Ciudad", "zona": "urbana",
                "problema_real_id": 1, "justificacion": "Test", "propuesta": "Test",
                "responsable": "alcaldia", "beneficiario": "todos"}
        with pytest.raises(ValidationError, match="Departamento inválido"):
            validate_participacion(data)

    def test_municipio_requerido(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "", "zona": "urbana",
                "problema_real_id": 1, "justificacion": "Test", "propuesta": "Test",
                "responsable": "alcaldia", "beneficiario": "todos"}
        with pytest.raises(ValidationError, match="municipio es requerido"):
            validate_participacion(data)

    def test_zona_invalida(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "costera",
                "problema_real_id": 1, "justificacion": "Test", "propuesta": "Test",
                "responsable": "alcaldia", "beneficiario": "todos"}
        with pytest.raises(ValidationError, match="Zona inválida"):
            validate_participacion(data)


class TestValidateProblema:

    def test_problema_requerido(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "justificacion": "Test", "propuesta": "Test",
                "responsable": "alcaldia", "beneficiario": "todos"}
        with pytest.raises(ValidationError, match="seleccionar un problema"):
            validate_participacion(data)


class TestValidateTextos:

    def test_justificacion_requerida(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_real_id": 1, "justificacion": "", "propuesta": "Test",
                "responsable": "alcaldia", "beneficiario": "todos"}
        with pytest.raises(ValidationError, match="justificación es requerida"):
            validate_participacion(data)

    def test_propuesta_requerida(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_real_id": 1, "justificacion": "Test", "propuesta": "",
                "responsable": "alcaldia", "beneficiario": "todos"}
        with pytest.raises(ValidationError, match="propuesta es requerida"):
            validate_participacion(data)

    def test_justificacion_max_500(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_real_id": 1, "justificacion": "x" * 501, "propuesta": "Test",
                "responsable": "alcaldia", "beneficiario": "todos"}
        with pytest.raises(ValidationError, match="máximo 500"):
            validate_participacion(data)

    def test_propuesta_max_500(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_real_id": 1, "justificacion": "Test", "propuesta": "x" * 501,
                "responsable": "alcaldia", "beneficiario": "todos"}
        with pytest.raises(ValidationError, match="máximo 500"):
            validate_participacion(data)


class TestValidateGobernanza:

    def test_responsable_requerido(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_real_id": 1, "justificacion": "Test", "propuesta": "Test",
                "beneficiario": "todos"}
        with pytest.raises(ValidationError, match="debería liderar"):
            validate_participacion(data)

    def test_beneficiario_invalido(self):
        data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                "problema_real_id": 1, "justificacion": "Test", "propuesta": "Test",
                "responsable": "alcaldia", "beneficiario": "gatitos"}
        with pytest.raises(ValidationError, match="Beneficiario inválido"):
            validate_participacion(data)


class TestValidData:

    def test_data_valida_no_lanza_error(self, app):
        with app.app_context():
            from app.models.participacion import ProblemaReal
            if ProblemaReal.query.count() == 0:
                pytest.skip("No problemas in DB")

            data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                    "problema_real_id": 1, "justificacion": "Test justificación",
                    "propuesta": "Test propuesta", "responsable": "alcaldia",
                    "beneficiario": "todos"}
            result = validate_participacion(data)
            assert result["departamento"] == "Bogotá D.C."
            assert result["municipio"] == "Bogotá"
            assert result["zona"] == "urbana"

    def test_sanitizes_text(self, app):
        with app.app_context():
            from app.models.participacion import ProblemaReal
            if ProblemaReal.query.count() == 0:
                pytest.skip("No problemas in DB")

            data = {"departamento": "Bogotá D.C.", "municipio": "Bogotá", "zona": "urbana",
                    "problema_real_id": 1,
                    "justificacion": "<script>alert(1)</script>Justificación",
                    "propuesta": "<b>Propuesta</b>",
                    "responsable": "alcaldia", "beneficiario": "todos"}
            result = validate_participacion(data)
            assert "<script>" not in result["justificacion"]
            assert "<b>" not in result["propuesta"]
