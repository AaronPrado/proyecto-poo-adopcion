"""
Blueprint para la API REST.
Configura Flask-RESTX con Swagger automático.
"""

from flask import Blueprint
from flask_restx import Api

# Crear blueprint
bp = Blueprint('api', __name__, url_prefix='/api')

# Configurar Flask-RESTX (Swagger)
api = Api(
    bp,
    title='API Adopción de Mascotas',
    version='1.0',
    description='API REST para gestionar adopciones de mascotas',
    doc='/docs',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Escribe: Bearer <tu_token>'
        }
    },
    security='Bearer'  # Swagger UI en /api/docs
)

# Agregar namespaces a la API
from app.routes.api import auth, mascotas, solicitudes

api.add_namespace(auth.ns)
api.add_namespace(mascotas.ns)
api.add_namespace(solicitudes.ns)

# Desactivar X-Fields header en Swagger
api.mask_header = None