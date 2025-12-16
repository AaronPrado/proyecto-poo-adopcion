# Portal de Adopción de Mascotas🐾

Sistema web de gestión de adopciones para refugios de animales desarrollado con Flask y PostgreSQL.

## Descripción

Aplicación web que permite a un refugio de animales gestionar el proceso completo de adopción de mascotas, desde la publicación del catálogo hasta la aprobación de solicitudes.

### Funcionalidades principales:

- Sistema de autenticación (usuarios y administradores)
- Catálogo público de mascotas disponibles
- Solicitudes de adopción con cuestionario
- Notificaciones por email
- Panel de administración para gestión de mascotas y solicitudes
- Subida de fotos de mascotas

## Tecnologías

- **Backend:** Flask 3.0
- **Base de Datos:** PostgreSQL 15+
- **ORM:** SQLAlchemy
- **Templates:** Jinja2
- **Testing:** pytest + coverage
- **Despliegue:** Docker Compose (desarrollo) / Railway (producción)

## Instalación

### Requisitos previos:
- Python 3.11+
- Docker y Docker Compose (para desarrollo local)
- Git

### Pasos:

1. **Clonar el repositorio:**
```bash
git clone https://github.com/AaronPrado/proyecto-poo-adopcion.git
cd proyecto-poo-adopcion
```

2. **Instalar dependencias:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Levantar base de datos con Docker:**
```bash
docker compose up -d
```

4. **Ejecutar la aplicación:**
```bash
python run.py
```

La aplicación estará disponible en: http://localhost:5000

## Docker (Desarrollo)

### Levantar servicios:
```bash
docker compose up -d
```

Servicios disponibles:
- **PostgreSQL:** localhost:5432
- **Adminer:** http://localhost:8080

### Detener servicios:
```bash
docker compose down
```

## Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=app --cov-report=html
```

## 📁 Estructura del Proyecto

```
proyecto_final/
├── app/                    # Aplicación Flask
│   ├── models.py           # Modelos SQLAlchemy
│   ├── routes/             # Blueprints (auth, mascotas, solicitudes)
│   ├── templates/          # Plantillas Jinja2
│   └── static/             # CSS, JS, imágenes
├── scripts_bd/             # Scripts SQL de inicialización
├── tests/                  # Tests unitarios
├── docs/                   # Documentación técnica
├── docker-compose.yml      # Configuración Docker
├── requirements.txt        # Dependencias Python
└── run.py                  # Entry point
```

## Autor

Aarón Prado Darriba
