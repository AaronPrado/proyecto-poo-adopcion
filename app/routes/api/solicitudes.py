"""
Endpoints de solicitudes para la API.
"""

from flask import request, g
from flask_restx import Namespace, Resource, fields

from app import db
from app.models import Solicitud, Mascota
from app.routes.api.auth import jwt_required

ns = Namespace("solicitudes", description="Solicitudes")

# Modelos para Swagger
solicitud_model = ns.model('Solicitudes', {
    'id': fields.Integer(required=True, description='ID único de la solicitud'),
    'usuario_id': fields.Integer(required=True, description='ID único del usuario'),
    'mascota_id': fields.Integer(required=True, description='ID único de la mascota.'),
    'fecha_solicitud': fields.String(required=True, description='Fecha ISO de la solicitud'),
    'estado': fields.String(required=True, description='pendiente/aprobada/rechazada'),
    'fecha_revision': fields.String(required=True, description='Fecha ISO de la revisión'),
    'comentarios_admin': fields.String(required=True, description='Comentarios del administrador'),
    'cuestionario': fields.Raw(required=True, description='Cuestionario')
})

create_solicitud_model = ns.model('CrearSolicitud', {
    'mascota_id': fields.Integer(required=True, description='ID de la mascota'),
    'cuestionario': fields.Raw(description='Respuestas del cuestionario')
})

@ns.route("/mias")
class MisSolicitudes(Resource):
    @jwt_required
    @ns.marshal_list_with(solicitud_model)
    def get(self):
        """Devuelve las solicitudes del usuario actual"""
        query = Solicitud.query.filter_by(usuario_id=g.current_user.id)

        solicitudes = query.order_by(Solicitud.fecha_solicitud).all()
        return [s.to_dict() for s in solicitudes]

    
@ns.route("/")
class CrearSolicitud (Resource):
    @jwt_required
    @ns.expect(create_solicitud_model)
    @ns.response(201, 'Solicitud creada exitosamente', solicitud_model)
    def post(self):
        data = request.get_json()

        if not data or not data.get('mascota_id') or not data.get('cuestionario'):
            return {'error': 'Datos inválidos'}, 400
        
        mascota = Mascota.query.get(data['mascota_id'])
        if not mascota:
            return {'error': 'Mascota no encontrada'}, 404
        
        if mascota.estado != 'disponible':
            return {'error': 'Mascota no disponible'}, 400
        
        solicitud = Solicitud(
            usuario_id=g.current_user.id,
            mascota_id=data['mascota_id'],
            cuestionario=data['cuestionario']
        )
        db.session.add(solicitud)
        db.session.commit()
        return solicitud.to_dict(), 201
        
    
