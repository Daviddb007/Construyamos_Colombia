"""Tests unitarios para el motor SRIE."""
import pytest

from app.services.srie.matcher import buscar_pilar_por_problema
from app.services.srie.confidence import calcular_confianza
from app.services.srie.explanation import generar_explicacion


class TestMatcher:

    def test_seguridad_maps_to_seguridad(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Seguridad")
            assert pilar is not None
            assert "Seguridad" in pilar.nombre

    def test_educacion_maps_to_educacion(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Educación")
            assert pilar is not None
            assert "Educación" in pilar.nombre

    def test_salud_maps_to_salud(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Salud")
            assert pilar is not None
            assert "Salud" in pilar.nombre

    def test_corrupcion_maps_to_corrupcion(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Corrupción")
            assert pilar is not None
            assert "Corrupción" in pilar.nombre

    def test_campo_maps_to_campo(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Campo y agro")
            assert pilar is not None
            assert "Campo" in pilar.nombre or "Agro" in pilar.nombre

    def test_medioambiente_maps_to_medioambiente(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Medioambiente")
            assert pilar is not None
            assert "Medioambiente" in pilar.nombre

    def test_empleo_maps_to_minero(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Conseguir empleo")
            assert pilar is not None
            assert "Minero" in pilar.nombre or "Energét" in pilar.nombre

    def test_otro_returns_none(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Otro")
            assert pilar is None

    def test_unknown_returns_none(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("ProblemaInexistente")
            assert pilar is None


class TestConfidence:

    def test_seguridad_high_confidence(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Seguridad")
            conf = calcular_confianza("Seguridad", "Justificación", "Propuesta", pilar)
            assert conf >= 0.80

    def test_otro_zero_confidence(self, app):
        with app.app_context():
            conf = calcular_confianza("Otro", "Justificación", "Propuesta", None)
            assert conf == 0.0

    def test_long_text_bonus(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Seguridad")
            short = calcular_confianza("Seguridad", "Corto", "Corto", pilar)
            long_text = "x" * 150
            long = calcular_confianza("Seguridad", long_text, long_text, pilar)
            assert long >= short

    def test_confidence_range(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Seguridad")
            conf = calcular_confianza("Seguridad", "Test", "Test", pilar)
            assert 0.0 <= conf <= 1.0


class TestExplanation:

    def test_high_confidence_explanation(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Seguridad")
            exp = generar_explicacion("Seguridad", pilar, 0.95)
            assert "Seguridad" in exp
            assert "directamente" in exp

    def test_medium_confidence_explanation(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Seguridad")
            exp = generar_explicacion("Seguridad", pilar, 0.65)
            assert "parcialmente" in exp

    def test_low_confidence_explanation(self, app):
        with app.app_context():
            pilar = buscar_pilar_por_problema("Seguridad")
            exp = generar_explicacion("Seguridad", pilar, 0.30)
            assert "provisionalmente" in exp

    def test_no_pilar_explanation(self, app):
        with app.app_context():
            exp = generar_explicacion("Otro", None, 0.0)
            assert "revisión manual" in exp
