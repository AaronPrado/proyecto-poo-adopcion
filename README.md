# 🐾 Portal de Adopción de Mascotas

Aplicación web para la gestión integral de adopciones de mascotas desarrollada con **Flask**, como proyecto del módulo **POO** del Curso de Especialización Superior en Desarrollo de Aplicaciones en Python.





## Descripción

Los refugios de animales suelen gestionar las adopciones de forma manual, lo que genera ineficiencias y dificulta el seguimiento de las solicitudes.  
Este proyecto digitaliza todo el proceso de adopción mediante un portal web que permite:

- Consultar un catálogo público de mascotas
- Enviar solicitudes de adopción mediante un formulario online
- Hacer seguimiento del estado de las solicitudes
- Gestionar mascotas y solicitudes desde un panel de administración

---

## Funcionalidades

### Usuarios
- Registro e inicio de sesión
- Inicio de sesión con Google (OAuth 2.0)
- Autenticación segura con hash de contraseñas
- Historial de solicitudes
- Control de acceso por roles (administrador / adoptante)

### Mascotas
- Catálogo público de mascotas disponibles
- Vista detallada de cada mascota
- CRUD completo desde el panel de administración
- Subida de imágenes a AWS S3 o URL externa
- Cambio automático de estado según el proceso de adopción

### Solicitudes
- Formulario de solicitud con cuestionario de evaluación
- Gestión de estados (pendiente, aceptada, rechazada)
- Comentarios del administrador

---

## Tecnologías utilizadas

**Backend**
- Python 3.12
- Flask 3.0
- Flask-SQLAlchemy
- Flask-Login
- Authlib (Google OAuth)
- boto3 (AWS S3)
- Jinja2

**Base de datos**
- PostgreSQL 15

**Frontend**
- HTML5
- CSS3
- Bootstrap 5

**Infraestructura**
- Docker y Docker Compose (desarrollo)
- Railway (producción)
- Gunicorn

---

## Estructura del proyecto

```
/
├── app/
│   ├── models.py
│   ├── decorators.py
│   ├── s3.py
│   ├── routes/
│   ├── templates/
│   └── static/
├── docs/
├── scripts_bd/
├── tests/
├── config.py
├── run.py
├── docker-compose.yml
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

## Instalación y ejecución

### Requisitos
- Python 3.12
- Docker y Docker Compose

### Pasos

```bash
git clone https://github.com/AaronPrado/proyecto-poo-adopcion.git
cd proyecto-poo-adopcion
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
python run.py
```

Acceder a: http://localhost:5000

### Variables de entorno

Crea un archivo `.env` en la raíz del proyecto (ver `.env.example`):

```
# Google OAuth
GOOGLE_CLIENT_ID=tu_client_id
GOOGLE_CLIENT_SECRET=tu_client_secret

# AWS S3 (subida de imágenes)
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_S3_BUCKET=nombre_bucket
AWS_S3_REGION=eu-west-1
```

**Google OAuth:** Configura un proyecto en [Google Cloud Console](https://console.cloud.google.com/) con OAuth 2.0 y añade `http://localhost:5000/auth/google/callback` como URI de redirección.

**AWS S3:** Crea un bucket S3 con acceso público de lectura y un usuario IAM con permisos de PutObject, GetObject y DeleteObject.


### Detener servicios
```bash
docker compose down
```

---

## Tests

```bash
cd app

# Ejecutar tests
python -m pytest

# Con coverage en HTML
python -m pytest --cov=app --cov-report=html
```

---

## Autor

**Aarón Prado Darriba**  
