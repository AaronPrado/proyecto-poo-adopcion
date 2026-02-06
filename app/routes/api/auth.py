"""
Endpoints de autenticación para la API.
Login y decorador JWT.
"""

from functools import wraps
from datetime import datetime, timedelta

import jwt
from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields

from app.models import Usuario

# Namespace para auth
ns = Namespace('auth', description='Autenticación')

# Modelos para Swagger
login_model = ns.model('Login', {
    'email': fields.String(required=True, description='Email del usuario'),
    'password': fields.String(required=True, description='Contraseña')
})

token_response = ns.model('TokenResponse', {
    'token': fields.String(description='JWT token'),
    'user': fields.Raw(description='Datos del usuario')
})

error_response = ns.model('ErrorResponse', {
    'error': fields.String(description='Mensaje de error')
})


def generate_token(user_id):
    """Genera un JWT token para el usuario."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRATION_HOURS']),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


def jwt_required(f):
    """Decorador que requiere un JWT válido."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar token en header Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return {'error': 'Token no proporcionado'}, 401
        
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            g.current_user = Usuario.query.get(payload['user_id'])
            if not g.current_user:
                return {'error': 'Usuario no encontrado'}, 401
        except jwt.ExpiredSignatureError:
            return {'error': 'Token expirado'}, 401
        except jwt.InvalidTokenError:
            return {'error': 'Token inválido'}, 401
        
        return f(*args, **kwargs)
    return decorated


@ns.route('/login')
class Login(Resource):
    @ns.expect(login_model)
    @ns.response(200, 'Login exitoso', token_response)
    @ns.response(401, 'Credenciales inválidas', error_response)
    def post(self):
        """Autenticación de usuario, devuelve JWT."""
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return {'error': 'Email y password son requeridos'}, 400
        
        usuario = Usuario.query.filter_by(email=data['email']).first()
        
        if not usuario or not usuario.password_hash:
            return {'error': 'Credenciales inválidas'}, 401
        
        if not usuario.check_password(data['password']):
            return {'error': 'Credenciales inválidas'}, 401
        
        if not usuario.activo:
            return {'error': 'Cuenta desactivada'}, 401
        
        token = generate_token(usuario.id)
        
        return {
            'token': token,
            'user': usuario.to_dict()
        }, 200
