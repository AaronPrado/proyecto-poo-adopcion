"""
Configuración de la aplicación Flask por entornos.

Este módulo define las clases de configuración para diferentes entornos:
- Config: Configuración base
- DevelopmentConfig: Configuración para desarrollo local
- ProductionConfig: Configuración para producción (Railway)

Uso:
    from config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class Config:
    """
    Configuración base de Flask.

    Atributos compartidos por todos los entornos (desarrollo, producción).
    Las clases hijas heredan y pueden sobrescribir estos valores.
    """

    # SECRET_KEY: Clave secreta para sesiones, CSRF, cookies firmadas
    # IMPORTANTE: En producción debe ser una cadena aleatoria segura
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    # AWS S3
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_S3_REGION = os.environ.get('AWS_S3_REGION', 'eu-west-1')

    # SQLAlchemy: Desactivar tracking de modificaciones (ahorra memoria)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLAlchemy: Mostrar SQL queries en logs (útil para debugging)
    SQLALCHEMY_ECHO = False

    # Flask-Mail: Configuración de email
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@aaronpradoadopciones.com'

    # Upload de archivos: Extensiones permitidas para fotos
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Upload de archivos: Tamaño máximo de archivo (5MB en bytes)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB


class DevelopmentConfig(Config):
    """
    Configuración para entorno de desarrollo local.

    Características:
    - DEBUG activado (recargar automático + mensajes de error detallados)
    - Base de datos PostgreSQL en Docker (localhost:5432)
    - SQLAlchemy ECHO activado (ver queries SQL en consola)
    """

    DEBUG = True
    TESTING = False

    # Base de datos: PostgreSQL en Docker Compose (localhost)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://admin:password@localhost:5432/adopciones_db'

    # Mostrar queries SQL en desarrollo para debugging
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Configuración para entorno de producción (Railway).

    Características:
    - DEBUG desactivado (seguridad)
    - Base de datos PostgreSQL managed de Railway
    - SQLAlchemy ECHO desactivado (no contaminar logs)
    - SECRET_KEY obligatoria desde variable de entorno
    """

    DEBUG = False
    TESTING = False

    # Base de datos: PostgreSQL managed en Railway
    # Railway proporciona DATABASE_URL automáticamente
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # En producción no mostrar queries SQL
    SQLALCHEMY_ECHO = False

    # Validación: SECRET_KEY es obligatoria en producción
    @classmethod
    def init_app(cls, app):
        """
        Validaciones adicionales al iniciar la app en producción.

        Args:
            app: Instancia de Flask

        Raises:
            RuntimeError: Si SECRET_KEY no está configurada
        """
        Config.init_app(app)

        # Asegurar que SECRET_KEY esté configurada
        if not app.config['SECRET_KEY'] or app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            raise RuntimeError(
                'SECRET_KEY debe estar configurada en producción. '
                'Define la variable de entorno SECRET_KEY.'
            )


class TestingConfig(Config):
    """
    Configuración para tests unitarios con pytest.

    Características:
    - TESTING activado (deshabilita CSRF, etc.)
    - Base de datos SQLite en memoria (rápido, desechable)
    - WTF_CSRF_ENABLED desactivado (facilita tests de formularios)
    """

    DEBUG = False
    TESTING = True

    # Base de datos en memoria para tests (SQLite)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Desactivar CSRF para tests
    WTF_CSRF_ENABLED = False

    # No mostrar queries SQL en tests (ruido en output)
    SQLALCHEMY_ECHO = False


# Diccionario para seleccionar configuración por nombre
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
