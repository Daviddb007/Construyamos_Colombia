from flask import Blueprint, jsonify, render_template, request

from app import db
from app.models.integracion import Webhook

integraciones_bp = Blueprint('integraciones', __name__)


@integraciones_bp.route('/ecosistema')
def pagina():
    return render_template('integraciones.html')


@integraciones_bp.route('/api/webhooks', methods=['GET', 'POST'])
def api_webhooks():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        wh = Webhook(
            nombre=data.get('nombre', ''),
            url=data.get('url', ''),
            evento=data.get('evento', 'participacion.nueva'),
        )
        db.session.add(wh)
        db.session.commit()
        return jsonify(wh.to_dict()), 201

    webhooks = Webhook.query.order_by(Webhook.created_at.desc()).all()
    return jsonify([w.to_dict() for w in webhooks])


@integraciones_bp.route('/api/webhooks/<int:wh_id>', methods=['DELETE'])
def api_webhook_eliminar(wh_id):
    wh = Webhook.query.get_or_404(wh_id)
    db.session.delete(wh)
    db.session.commit()
    return jsonify({'exito': True})
