-- ==================================================
-- Portal de Adopción de Mascotas
-- ==================================================

-- Eliminar tablas si existen (para desarrollo)
DROP TABLE IF EXISTS solicitudes CASCADE;
DROP TABLE IF EXISTS mascotas CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;

-- TABLA: usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150),
    telefono VARCHAR(20),
    direccion TEXT,
    rol VARCHAR(20) NOT NULL DEFAULT 'adoptante'
        CHECK (rol IN ('adoptante', 'admin')),
    fecha_registro TIMESTAMP NOT NULL DEFAULT NOW(),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);

-- TABLA: mascotas
CREATE TABLE mascotas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    especie VARCHAR(50) NOT NULL,
    raza VARCHAR(100),
    edad_aprox INTEGER CHECK (edad_aprox >= 0),
    sexo VARCHAR(10) CHECK (sexo IN ('Macho', 'Hembra', 'Desconocido')),
    tamano VARCHAR(20) CHECK (tamano IN ('Pequeño', 'Mediano', 'Grande')),
    descripcion TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'disponible'
        CHECK (estado IN ('disponible', 'en_proceso', 'adoptado')),
    foto_url VARCHAR(255),
    fecha_ingreso TIMESTAMP NOT NULL DEFAULT NOW(),
    vacunado BOOLEAN NOT NULL DEFAULT FALSE,
    esterilizado BOOLEAN NOT NULL DEFAULT FALSE
);

-- Índices
CREATE INDEX idx_mascotas_estado ON mascotas(estado);
CREATE INDEX idx_mascotas_especie ON mascotas(especie);

-- TABLA: solicitudes
CREATE TABLE solicitudes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    mascota_id INTEGER NOT NULL REFERENCES mascotas(id) ON DELETE CASCADE,
    fecha_solicitud TIMESTAMP NOT NULL DEFAULT NOW(),
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente'
        CHECK (estado IN ('pendiente', 'aprobada', 'rechazada')),
    cuestionario_json JSONB,
    comentarios_admin TEXT,
    fecha_revision TIMESTAMP,
    revisado_por INTEGER REFERENCES usuarios(id),

    -- Un usuario no puede solicitar la misma mascota dos veces
    CONSTRAINT unique_usuario_mascota UNIQUE (usuario_id, mascota_id)
);

-- Índices
CREATE INDEX idx_solicitudes_usuario ON solicitudes(usuario_id);
CREATE INDEX idx_solicitudes_mascota ON solicitudes(mascota_id);
CREATE INDEX idx_solicitudes_estado ON solicitudes(estado);

-- Comentarios en tablas (documentación)
COMMENT ON TABLE usuarios IS 'Usuarios del sistema (adoptantes y administradores)';
COMMENT ON TABLE mascotas IS 'Mascotas disponibles para adopción';
COMMENT ON TABLE solicitudes IS 'Solicitudes de adopción realizadas por usuarios';

COMMENT ON COLUMN solicitudes.cuestionario_json IS 'Respuestas del formulario de adopción en formato JSON';