"""Punto de entrada para la aplicación.

Uso:
    python run.py              # Servidor de desarrollo
    flask seed                 # Sembrar datos iniciales (plan + catálogos)
    flask init-db              # Crear tablas sin seed
    flask db migrate           # Generar migración
    flask db upgrade           # Aplicar migración
"""
import os

from app import create_app, db


app = create_app(os.environ.get("FLASK_CONFIG", "development"))


@app.cli.command("seed")
def seed_command():
    """Crea tablas y siembra datos iniciales (plan + sectores + actores + beneficiarios)."""
    with app.app_context():
        db.create_all()
        from app.seed import run_all

        run_all()


@app.cli.command("init-db")
def init_db_command():
    """Crea todas las tablas sin sembrar datos."""
    with app.app_context():
        db.create_all()
        print("Tablas creadas exitosamente.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=app.config.get("PORT", 5000))
