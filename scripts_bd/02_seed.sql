-- Script de datos de prueba para el portal de adopciones
-- Las contraseñas son hashes de ejemplo. Se deben regenerar al crear usuarios reales.

TRUNCATE TABLE solicitudes, mascotas, usuarios RESTART IDENTITY CASCADE;

-- USUARIOS (password para todos: "password123" - hashes de ejemplo)
INSERT INTO usuarios (email, password_hash, nombre, apellidos, telefono, direccion, rol, fecha_registro) VALUES
('admin@refugio.com', 'scrypt:32768:8:1$Hash1$abc123', 'María', 'García López', '666111222', 'Calle del Refugio 1, Madrid', 'admin', NOW()),
('juan.perez@email.com', 'scrypt:32768:8:1$Hash2$def456', 'Juan', 'Pérez Martín', '666222333', 'Calle Mayor 10, Madrid', 'adoptante', NOW()),
('ana.lopez@email.com', 'scrypt:32768:8:1$Hash3$ghi789', 'Ana', 'López Fernández', '666333444', 'Avenida Paz 25, Barcelona', 'adoptante', NOW()),
('carlos.ruiz@email.com', 'scrypt:32768:8:1$Hash4$jkl012', 'Carlos', 'Ruiz Sánchez', '666444555', 'Plaza España 5, Valencia', 'adoptante', NOW());

-- MASCOTAS
INSERT INTO mascotas (nombre, especie, raza, edad_aproximada, sexo, tamano, peso_kg, color, descripcion, historia, necesidades_especiales, estado, fecha_ingreso, foto_url) VALUES
('Calcetines', 'Perro', 'Labrador', 3, 'H', 'Grande', 28.5, 'Dorado', 'Perra cariñosa y juguetona.', 'Encontrada abandonada en parque.', 'Ejercicio diario y jardín grande.', 'disponible', '2024-01-15', 'default_perro.jpg'),
('Zeus', 'Perro', 'Pastor Alemán', 5, 'M', 'Grande', 35.0, 'Negro y marrón', 'Perro leal e inteligente.', 'Su dueño falleció.', 'Actividad física diaria.', 'disponible', '2024-02-10', 'default_perro.jpg'),
('Toby', 'Perro', 'Beagle', 2, 'M', 'Mediano', 12.0, 'Tricolor', 'Perro activo y curioso.', 'Rescatado de maltrato.', 'Paseos largos.', 'en_proceso', '2024-03-05', 'default_perro.jpg'),
('Bella', 'Perro', 'Mestizo', 4, 'H', 'Pequeño', 8.5, 'Blanco y negro', 'Perrita tranquila.', 'Familia se mudó.', 'Ninguna especial.', 'disponible', '2024-02-20', 'default_perro.jpg'),
('Misi', 'Gato', 'Siamés', 2, 'H', 'Pequeño', 3.5, 'Crema', 'Gata vocal y sociable.', 'Abandonada de cachorro.', 'Cepillado regular.', 'disponible', '2024-01-20', 'default_gato.jpg'),
('Guantes', 'Gato', 'Europeo', 6, 'M', 'Pequeño', 4.8, 'Gris', 'Gato independiente.', 'Rescatado de calle.', 'Salir al exterior.', 'disponible', '2023-12-10', 'default_gato.jpg'),
('Nala', 'Gato', 'Persa', 3, 'H', 'Pequeño', 4.0, 'Blanco', 'Gata elegante.', 'Dueña en residencia.', 'Cepillado diario.', 'disponible', '2024-02-15', 'default_gato.jpg'),
('Lys', 'Conejo', 'Belier', 2, 'M', 'Pequeño', 2.0, 'Blanco', 'Conejo dócil.', 'Niño perdió interés.', 'Jaula amplia.', 'disponible', '2024-03-01', 'default_conejo.jpg');

-- SOLICITUDES
INSERT INTO solicitudes (usuario_id, mascota_id, estado, cuestionario_json, fecha_solicitud, comentarios_admin, fecha_revision, revisado_por) VALUES
(2, 3, 'aprobada', '{"experiencia": "Si, Beagle antes", "vivienda": "Casa con jardin"}', '2024-03-10 10:30:00', 'Perfil excelente.', '2024-03-11 14:20:00', 1),
(3, 1, 'pendiente', '{"experiencia": "No", "vivienda": "Piso con terraza"}', '2024-03-15 16:45:00', NULL, NULL, NULL),
(4, 2, 'rechazada', '{"experiencia": "No", "vivienda": "Piso pequeño"}', '2024-03-08 09:15:00', 'Espacio insuficiente.', '2024-03-09 11:30:00', 1);
