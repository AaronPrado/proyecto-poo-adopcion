> Portal de Adopción de Mascotas - Documentación

---

## Diagrama UML de Clases Python

```
┌─────────────────────────────────────────────────────┐
│                    Usuario                          │
│              (hereda de UserMixin)                  │
├─────────────────────────────────────────────────────┤
│ - id: int                                           │
│ - email: str                                        │
│ - password_hash: str (nullable)                     │
│ - nombre: str                                       │
│ - apellidos: str                                    │
│ - telefono: str                                     │
│ - direccion: str                                    │
│ - rol: str                                          │
│ - fecha_registro: datetime                          │
│ - activo: bool                                      │
│ - oauth_provider: str                               │
│ - oauth_id: str (unique)                            │
│ - solicitudes: List[Solicitud]  (relación 1:N)      │
│ - solicitudes_revisadas: List[Solicitud] (relación) │
├─────────────────────────────────────────────────────┤
│ + __init__(email, nombre, password=None, **kwargs)  │
│ + set_password(password: str) -> None               │
│ + check_password(password: str) -> bool             │
│ + is_admin() -> bool                                │
│ + __repr__() -> str                                 │
└─────────────────────────────────────────────────────┘
              │ 1
              │
              │ N
              ▼
┌─────────────────────────────────────────────────────┐
│                   Solicitud                         │
├─────────────────────────────────────────────────────┤
│ - id: int                                           │
│ - usuario_id: int (FK -> Usuario)                   │
│ - mascota_id: int (FK -> Mascota)                   │
│ - fecha_solicitud: datetime                         │
│ - estado: str                                       │
│ - cuestionario_json: dict                           │
│ - comentarios_admin: str                            │
│ - fecha_revision: datetime                          │
│ - revisado_por: int (FK -> Usuario)                 │
│ - usuario: Usuario (relación N:1)                   │
│ - mascota: Mascota (relación N:1)                   │
│ - revisor: Usuario (relación N:1)                   │
├─────────────────────────────────────────────────────┤
│ + __init__(usuario_id, mascota_id, cuestionario)    │
│ + aprobar(admin_id, comentario) -> None             │
│ + rechazar(admin_id, comentario) -> None            │
│ + esta_pendiente() -> bool                          │
│ + __repr__() -> str                                 │
└─────────────────────────────────────────────────────┘
              │ N
              │
              │ 1
              ▼
┌─────────────────────────────────────────────────────┐
│                    Mascota                          │
├─────────────────────────────────────────────────────┤
│ - id: int                                           │
│ - nombre: str                                       │
│ - especie: str                                      │
│ - raza: str                                         │
│ - edad_aprox: int                                   │
│ - sexo: str                                         │
│ - tamano: str                                       │
│ - descripcion: str                                  │
│ - estado: str                                       │
│ - foto_url: str                                     │
│ - fecha_ingreso: datetime                           │
│ - vacunado: bool                                    │
│ - esterilizado: bool                                │
│ - solicitudes: List[Solicitud] (relación 1:N)       │
├─────────────────────────────────────────────────────┤
│ + __init__(nombre, especie, descripcion)            │
│ + esta_disponible() -> bool                         │
│ + marcar_en_proceso() -> None                       │
│ + marcar_adoptado() -> None                         │
│ + tiene_solicitudes_pendientes() -> bool            │
│ + __repr__() -> str                                 │
└─────────────────────────────────────────────────────┘
```

---

## Diagrama de Base de Datos (PostgreSQL)

```
┌─────────────────────────┐
│      USUARIOS           │
├─────────────────────────┤
│ PK id                   │
│    email (UNIQUE)       │
│    password_hash        │
│    nombre               │
│    apellidos            │
│    telefono             │
│    direccion            │
│    rol                  │
│    fecha_registro       │
│    activo               │
│    oauth_provider       │
│    oauth_id (UNIQUE)    │
└─────────────────────────┘
         │ 1
         │
         │ N
         │
┌─────────────────────────┐       ┌─────────────────────────┐
│     SOLICITUDES         │   N   │      MASCOTAS           │
├─────────────────────────┤ ───── ├─────────────────────────┤
│ PK id                   │   1   │ PK id                   │
│ FK usuario_id           │       │    nombre               │
│ FK mascota_id           │       │    especie              │
│    fecha_solicitud      │       │    raza                 │
│    estado               │       │    edad_aprox           │
│    cuestionario_json    │       │    sexo                 │
│    comentarios_admin    │       │    tamano               │
│    fecha_revision       │       │    descripcion          │
│ FK revisado_por         │       │    estado               │
└─────────────────────────┘       │    foto_url             │
                                  │    fecha_ingreso        │
                                  │    vacunado             │
                                  │    esterilizado         │
                                  └─────────────────────────┘
```

---

## Conceptos POO

### 1. Encapsulación
- **Atributos privados:** `Usuario.password_hash` no se accede directamente
- **Métodos públicos:** `set_password()` y `check_password()` controlan el acceso
- **Validación:** Los métodos validan datos antes de modificar atributos

### 2. Abstracción
- **Métodos de alto nivel:** `aprobar()`, `rechazar()`, `marcar_adoptado()`
- **Separación de responsabilidades:** Cada clase tiene una función clara

### 3. Polimorfismo
- **Comportamiento según rol:** `Usuario.is_admin()` devuelve distinto valor
- **Métodos sobrescritos:** `__repr__()` personalizado en cada clase

### 4. Herencia
- **UserMixin:** `Usuario` hereda de `UserMixin` (Flask-Login)
- **Templates Jinja2:** `base.html` es extendido por otras plantillas

### 5. Decoradores
- **@admin_required:** Decorador personalizado en `app/decorators.py`
- Usa `functools.wraps` para preservar metadatos de la función
- Verifica rol de administrador en rutas protegidas

### 6. Relaciones
- **1:N (uno a muchos):**
  - Un usuario puede tener muchas solicitudes
  - Una mascota puede tener muchas solicitudes
- **N:1 (muchos a uno):**
  - Muchas solicitudes pertenecen a un usuario
  - Muchas solicitudes pertenecen a una mascota


## Estructura de Módulos Flask

```
app/
├── __init__.py          # Application Factory (crea instancia Flask)
│                        # Inicializa extensiones (db, mail, oauth)
│                        # Registra blueprints, error handlers
│
├── models.py            # Modelos SQLAlchemy (Usuario, Mascota, Solicitud)
├── decorators.py        # Decoradores personalizados (@admin_required)
├── s3.py                # Helper AWS S3 (upload_to_s3, delete_from_s3)
│
├── routes/              # Blueprints (rutas organizadas por funcionalidad)
│   ├── auth.py          # Login, registro, logout, OAuth Google
│   ├── mascotas.py      # CRUD mascotas + catálogo + S3 upload
│   ├── solicitudes.py   # Crear y revisar solicitudes
│   └── api/             # API REST (Flask-RESTX)
│       ├── __init__.py  # Blueprint API + Swagger config
│       ├── auth.py      # Login JWT, decorador @jwt_required
│       ├── mascotas.py  # GET mascotas (público)
│       └── solicitudes.py # POST/GET solicitudes (protegido)
│
├── templates/           # Plantillas Jinja2 (con herencia)
│   ├── base.html        # Plantilla base (navbar + footer + blocks)
│   ├── index.html       # Página de inicio
│   ├── auth/
│   │   ├── login.html
│   │   └── registro.html
│   ├── mascotas/
│   │   ├── catalogo.html
│   │   ├── detalle.html
│   │   └── form.html
│   └── solicitudes/
│       ├── crear.html
│       ├── mis_solicitudes.html
│       └── admin_solicitudes.html
│
└── static/              # Archivos estáticos
    └── css/
        └── styles.css
```

---

## Integración AWS S3

Las imágenes de mascotas se almacenan en AWS S3:

- **`app/s3.py`**: Módulo helper con funciones `upload_to_s3()` y `delete_from_s3()`
- **Validación**: Extensiones permitidas (png, jpg, jpeg, gif, webp) y tamaño máximo (5MB)
- **Nombres únicos**: UUID para evitar colisiones
- **Limpieza automática**: Al editar/eliminar mascota se borra la imagen antigua de S3

---

## API REST

API RESTful con autenticación JWT y documentación Swagger automática.

### Endpoints

| Método | Endpoint | Protegido | Descripción |
|--------|----------|-----------|-------------|
| POST | `/api/auth/login` | No | Login, devuelve JWT |
| GET | `/api/mascotas` | No | Lista mascotas disponibles |
| GET | `/api/mascotas/<id>` | No | Detalle de mascota |
| POST | `/api/solicitudes` | JWT | Crear solicitud de adopción |
| GET | `/api/solicitudes/mias` | JWT | Mis solicitudes |

### Autenticación JWT

1. El cliente hace POST a `/api/auth/login` con email y password
2. El servidor devuelve un token JWT
3. El cliente incluye el token en las peticiones protegidas: `Authorization: Bearer <token>`
4. El decorador `@jwt_required` valida el token y extrae el usuario

### Swagger UI

Documentación interactiva disponible en `/api/docs`:
- Prueba de endpoints
- Modelos de request/response
- Autenticación integrada
