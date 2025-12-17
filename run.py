"""
Este archivo es el punto de entrada para ejecutar la aplicación.
Utiliza el Application Factory pattern para crear la instancia de Flask.

Uso:
    python run.py

    O con variables de entorno:
    FLASK_ENV=development python run.py
    FLASK_ENV=production python run.py
"""

import os
from app import create_app

# Obtener el entorno desde variable de entorno (development por defecto)
config_name = os.environ.get("FLASK_ENV") or "development"

# Crear la aplicación usando el Application Factory
app = create_app(config_name)

if __name__ == "__main__":
    """
    Ejecutar la aplicación Flask.

    En desarrollo:
    - Debug activado (recarga automática)
    - Host 0.0.0.0 (accesible desde red local)
    - Puerto 5000

    En producción:
    - Usar gunicorn o waitress (no flask run directamente)
    - Ejemplo: gunicorn -w 4 -b 0.0.0.0:8000 run:app
    """
    app.run(
        host="0.0.0.0",  # Accesible desde cualquier interfaz de red
        port=5000,       # Puerto por defecto de Flask
        debug=app.config["DEBUG"]  # Debug según configuración
    )

