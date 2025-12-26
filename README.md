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
- Autenticación segura con hash de contraseñas
- Historial de solicitudes
- Control de acceso por roles (administrador / adoptante)

### Mascotas
- Catálogo público de mascotas disponibles
- Vista detallada de cada mascota
- CRUD completo desde el panel de administración
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
docker compose up -d
python run.py
```

Acceder a: http://localhost:5000

### Detener serivicios
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
