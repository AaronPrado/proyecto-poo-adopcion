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

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import config

# Inicializar extensiones (sin vincular a app todavía)
db = SQLAlchemy()
mail = Mail()


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

    # Importar modelos
    from app import models

    # Registrar blueprints (rutas)
    # Descomentar cuando se creen los blueprints
    # from app.routes import auth, mascotas, solicitudes
    # app.register_blueprint(auth.bp)
    # app.register_blueprint(mascotas.bp)
    # app.register_blueprint(solicitudes.bp)

    # Crear tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()

    # Ruta de prueba (temporal, eliminar cuando haya rutas reales)
    @app.route('/')
    def index():
        """Ruta temporal de bienvenida."""
        return '''
        <h1>Portal de Adopción de Mascotas</h1>
        <p>TExto de ejemplo</p>
        <p>Configuración activa: {}</p>
        '''.format(config_name)

    return app
