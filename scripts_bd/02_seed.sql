-- Script de datos de prueba para el portal de adopciones
-- Las contraseñas son hashes de ejemplo. Se deben regenerar al crear usuarios reales.

TRUNCATE TABLE solicitudes, mascotas, usuarios RESTART IDENTITY CASCADE;

-- USUARIOS (password para todos: "password123" - hashes de ejemplo)
INSERT INTO usuarios (email, password_hash, nombre, apellidos, telefono, direccion, rol, fecha_registro, activo) VALUES
('admin@refugio.com', 'scrypt:32768:8:1$DKaatGx2kbBBkbs4$71559ddc10a74c3beea51cfeb35b5faf7e5b71f24bb98b213ed09b3c1da5a4843a568f3ac1e119d2a1bd59b4e8b46a02e7583f835cebf0503b975dcc9d763f02', 'María', 'García López', '666111222', 'Calle del Refugio 1, Madrid', 'admin', NOW(), TRUE),
('juan.perez@email.com', 'scrypt:32768:8:1$ezT7AdZDhLjZpa5H$c6f6cd7b79eddcd14bab6a5c7cd1db2f9c27a122676b8a9589d60db34096c102400c14ea991d819761af8bd7f112a8db45bf78285dc5ebfed080828750072531', 'Juan', 'Pérez Martín', '666222333', 'Calle Mayor 10, Madrid', 'adoptante', NOW(), TRUE),
('ana.lopez@email.com', 'scrypt:32768:8:1$QG86zDLXB8xCs4qh$2e3f9d05023e54a55c54672718b4e2ef2c3d1bbcc3c96b3f91e143b9f1297cef31c704a5d5561777eb0a21547d2231dd74b90f70396dd44e225afbbd032c4237', 'Ana', 'López Fernández', '666333444', 'Avenida Paz 25, Barcelona', 'adoptante', NOW(), TRUE),
('carlos.ruiz@email.com', 'scrypt:32768:8:1$3g8SoRdlnidS6RbJ$2449c2e9a763d2149ddc9e2515296e214b454e72343c313716bb9e2160b7d25e586bbf63e5f8377bf28ee82fa7bab713b81ee985dec2a8ebe05b5daae4a5f941', 'Carlos', 'Ruiz Sánchez', '666444555', 'Plaza España 5, Valencia', 'adoptante', NOW(), TRUE);

-- MASCOTAS
INSERT INTO mascotas (nombre, especie, raza, edad_aprox, sexo, tamano, descripcion, estado, fecha_ingreso, foto_url, vacunado, esterilizado) VALUES
('Calcetines', 'Perro', 'Labrador', 3, 'Hembra', 'Grande', 'Perra cariñosa y juguetona de color dorado. Encontrada abandonada en un parque. Necesita ejercicio diario y jardín grande.', 'disponible', '2024-01-15', 'https://images.unsplash.com/photo-1558788353-f76d92427f16?w=400', TRUE, TRUE),
('Zeus', 'Perro', 'Pastor Alemán', 5, 'Macho', 'Grande', 'Perro leal e inteligente de color negro y marrón. Su dueño falleció. Necesita actividad física diaria.', 'disponible', '2024-02-10', 'https://images.unsplash.com/photo-1568572933382-74d440642117?w=400', TRUE, TRUE),
('Toby', 'Perro', 'Beagle', 2, 'Macho', 'Mediano', 'Perro activo y curioso de color tricolor. Rescatado de maltrato. Necesita paseos largos.', 'en_proceso', '2024-03-05', 'https://images.unsplash.com/photo-1505628346881-b72b27e84530?w=400', TRUE, FALSE),
('Bella', 'Perro', 'Mestizo', 4, 'Hembra', 'Pequeño', 'Perrita tranquila de color blanco y negro. Su familia se mudó y no pudo llevarla. No tiene necesidades especiales.', 'disponible', '2024-02-20', 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400', TRUE, TRUE),
('Misi', 'Gato', 'Siamés', 2, 'Hembra', 'Pequeño', 'Gata vocal y sociable de color crema. Abandonada cuando era cachorro. Necesita cepillado regular.', 'disponible', '2024-01-20', 'https://images.unsplash.com/photo-1513360371669-4adf3dd7dff8?w=400', TRUE, TRUE),
('Guantes', 'Gato', 'Europeo', 6, 'Macho', 'Pequeño', 'Gato independiente de color gris. Rescatado de la calle. Le gusta salir al exterior.', 'disponible', '2023-12-10', 'https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400', TRUE, TRUE),
('Nala', 'Gato', 'Persa', 3, 'Hembra', 'Pequeño', 'Gata elegante de color blanco. Su dueña tuvo que ir a una residencia. Necesita cepillado diario.', 'disponible', '2024-02-15', 'https://images.unsplash.com/photo-1495360010541-f48722b34f7d?w=400', TRUE, TRUE),
('Lys', 'Conejo', 'Belier', 2, 'Macho', 'Pequeño', 'Conejo dócil de color blanco. El niño perdió interés en cuidarlo. Necesita jaula amplia.', 'disponible', '2024-03-01', 'https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=400', TRUE, FALSE);

-- SOLICITUDES
INSERT INTO solicitudes (usuario_id, mascota_id, estado, cuestionario_json, fecha_solicitud, comentarios_admin, fecha_revision, revisado_por) VALUES
(2, 3, 'aprobada', '{"experiencia": "Si, Beagle antes", "vivienda": "Casa con jardin"}', '2024-03-10 10:30:00', 'Perfil excelente.', '2024-03-11 14:20:00', 1),
(3, 1, 'pendiente', '{"experiencia": "No", "vivienda": "Piso con terraza"}', '2024-03-15 16:45:00', NULL, NULL, NULL),
(4, 2, 'rechazada', '{"experiencia": "No", "vivienda": "Piso pequeño"}', '2024-03-08 09:15:00', 'Espacio insuficiente.', '2024-03-09 11:30:00', 1);
