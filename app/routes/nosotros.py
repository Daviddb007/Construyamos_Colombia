from flask import Blueprint, render_template

from app.models.miembro import MiembroEquipo

nosotros_bp = Blueprint('nosotros', __name__)


@nosotros_bp.route('/nosotros')
def pagina():
    miembros = MiembroEquipo.activos()
    return render_template('nosotros.html', miembros=miembros)
