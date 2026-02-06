"""
Endpoints públicos de mascotas para la API.
"""

from flask import request
from flask_restx import Namespace, Resource, fields

from app.models import Mascota

ns = Namespace("mascotas", description="Mascotas")

# Modelos para Swagger
mascota_model = ns.model('Mascotas', {
    'id': fields.Integer(required=True, description='ID único'),
    'nombre': fields.String(required=True, description='Nombre de la mascota'),
    'especie': fields.String(required=True, description='Perro, Gato, etc.'),
    'raza': fields.String(required=True, description='Raza'),
    'edad_aprox': fields.Integer(required=True, description='Edad aproximada en años'),
    'sexo': fields.String(required=True, description='Macho/Hembra'),
    'tamano': fields.String(required=True, description='Pequeño/Mediano/Grande'),
    'descripcion': fields.String(required=True, description='Descripción'),
    'estado': fields.String(required=True, description='disponible/en_proceso/adoptado'),
    'foto_url': fields.String(required=True, description='URL de la imagen'),
    'fecha_ingreso': fields.String(required=True, description='Fecha ISO'),
    'vacunado': fields.Boolean(required=True, description='Estado vacunación'),
    'esterilizado': fields.Boolean(required=True, description='Estado esterilización')
})

@ns.route("/")
class MascotaList(Resource):
    @ns.marshal_list_with(mascota_model)
    @ns.doc(params={
        'especie': 'Filtrar por especie (Perro, Gato...)',
        'raza': 'Filtrar por raza (Golden Retriever, Siamés...)',
        'edad_aprox': 'Filtrar por años (1, 3...)',
        'tamano': 'Filtrar por tamaño (Pequeño, Mediano, Grande)'
    })

    def get(self):
        """Lista todas las mascotas disponibles para adopción."""
        query = Mascota.query.filter_by(estado='disponible')

        # Filtros opcionales desde query params
        especie = request.args.get("especie")
        if especie:
            query = query.filter_by(especie=especie)

        raza = request.args.get("raza")
        if raza:
            query = query.filter_by(raza=raza)

        edad_aprox = request.args.get("edad_aprox")
        if edad_aprox:
            query = query.filter_by(edad_aprox=edad_aprox)

        tamano = request.args.get('tamano')
        if tamano:
            query = query.filter_by(tamano=tamano)
        
        mascotas = query.order_by(Mascota.fecha_ingreso.desc()).all()
        return [m.to_dict() for m in mascotas]


@ns.route("/<int:id>")
class MascotaDetail(Resource):
    @ns.marshal_with(mascota_model)
    @ns.response(404, 'Mascota no encontrada')
    def get(self, id):
        """Obtiene el detalle de una mascota por ID."""
        mascota = Mascota.query.get_or_404(id)
        return mascota.to_dict()