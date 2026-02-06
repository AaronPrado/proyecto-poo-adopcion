"""
Application Factory de Flask.

Este módulo implementa el patrón Application Factory para crear instancias
de la aplicación Flask con diferentes configuraciones.

Ventajas del Application Factory:
- Permite crear múltiples instancias de la app (testing, desarrollo, producción)
- Facilita los tests unitarios
- Evita imports circulares
- Permite configurar extensiones antes de crear la app

Uso:
    from app import create_app
    app = create_app('development')
    app.run()
"""

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from config import config
from authlib.integrations.flask_client import OAuth

# Inicializar extensiones (sin vincular a app todavía)
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
oauth = OAuth()


def create_app(config_name='default'):
    """
    Application Factory: Crea y configura una instancia de Flask.

    Este patrón permite crear múltiples instancias de la aplicación con
    diferentes configuraciones (desarrollo, testing, producción).

    Args:
        config_name (str): Nombre de la configuración a usar.
                           Opciones: 'development', 'production', 'testing', 'default'

    Returns:
        Flask: Instancia configurada de la aplicación Flask
    """

    # Crear instancia de Flask
    app = Flask(__name__)

    # Cargar configuración desde config.py
    app.config.from_object(config[config_name])

    # Inicializar extensiones con la app
    db.init_app(app)
    mail.init_app(app)

    # Configurar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Ruta de login
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

    # Configurar OAuth
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    # Importar modelos
    from app import models

    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """
        Callback requerido por Flask-Login para cargar un usuario.

        Args:
            user_id (str): ID del usuario como string

        Returns:
            Usuario: Instancia del usuario o None
        """
        return models.Usuario.query.get(int(user_id))

    # Registrar blueprints (rutas)
    from app.routes import auth, mascotas, solicitudes
    from app.routes.api import bp as api_bp
    app.register_blueprint(auth.bp)
    app.register_blueprint(mascotas.bp)
    app.register_blueprint(solicitudes.bp)
    app.register_blueprint(api_bp)

    # Crear tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()

    # Error handler para archivos demasiado grandes
    @app.errorhandler(413)
    def file_too_large(e):
        flash('El archivo es demasiado grande. Máximo 5MB.', 'danger')
        return redirect(request.url), 413


    # Ruta de inicio
    @app.route('/')
    def index():
        """
        Página de inicio del portal.

        Muestra estadísticas, mascotas destacadas y el proceso de adopción.
        """
        from app.models import Mascota, Usuario

        # Obtener estadísticas
        total_mascotas = Mascota.query.filter_by(estado='disponible').count()
        total_adoptadas = Mascota.query.filter_by(estado='adoptado').count()
        total_usuarios = Usuario.query.filter_by(rol='adoptante').count()

        # Obtener 3 mascotas destacadas (las más recientes disponibles)
        mascotas_destacadas = Mascota.query.filter_by(estado='disponible')\
            .order_by(Mascota.id.desc())\
            .limit(3)\
            .all()

        return render_template('index.html',
                             total_mascotas=total_mascotas,
                             total_adoptadas=total_adoptadas,
                             total_usuarios=total_usuarios,
                             mascotas_destacadas=mascotas_destacadas)

    return app