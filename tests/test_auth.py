"""
Tests para el módulo de autenticación (auth).

Tests incluidos:
- Registro de usuarios
- Login/logout
- Validaciones de formularios
- Protección de rutas
"""

import pytest
from app.models import Usuario
from app import db


class TestRegistro:
    """Tests para el registro de usuarios."""

    def test_registro_usuario_exitoso(self, client):
        """Test: Registro de un nuevo usuario con datos válidos."""
        response = client.post('/auth/registro', data={
            'nombre': 'Test User',
            'apellidos': 'Test Apellidos',
            'email': 'test@example.com',
            'telefono': '612345678',
            'direccion': 'Calle Test 123',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Cuenta creada exitosamente' in response.data.decode()

        # Verificar que el usuario se creó en la BD
        usuario = Usuario.query.filter_by(email='test@example.com').first()
        assert usuario is not None
        assert usuario.nombre == 'Test User'
        assert usuario.rol == 'adoptante'

    def test_registro_email_duplicado(self, client, usuario_adoptante):
        """Test: Intento de registro con email ya existente."""
        response = client.post('/auth/registro', data={
            'nombre': 'Otro Usuario',
            'apellidos': 'Otros Apellidos',
            'email': 'adoptante@test.com',  # Email ya existe
            'telefono': '612345679',
            'direccion': 'Calle Test 456',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'ya está registrado' in response.data.decode()

    def test_registro_passwords_no_coinciden(self, client):
        """Test: Intento de registro con contraseñas que no coinciden."""
        response = client.post('/auth/registro', data={
            'nombre': 'Test User',
            'apellidos': 'Test Apellidos',
            'email': 'test2@example.com',
            'telefono': '612345678',
            'direccion': 'Calle Test 123',
            'password': 'password123',
            'password2': 'diferente123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'no coinciden' in response.data.decode()

        # Verificar que NO se creó el usuario
        usuario = Usuario.query.filter_by(email='test2@example.com').first()
        assert usuario is None

    def test_registro_get_muestra_formulario(self, client):
        """Test: GET a /auth/registro muestra el formulario."""
        response = client.get('/auth/registro')

        assert response.status_code == 200
        assert 'Registro' in response.data.decode()
        assert 'email' in response.data.decode()
        assert 'password' in response.data.decode()


class TestLogin:
    """Tests para login de usuarios."""

    def test_login_exitoso(self, client, usuario_adoptante):
        """Test: Login con credenciales válidas."""
        response = client.post('/auth/login', data={
            'email': 'adoptante@test.com',
            'password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Bienvenido' in response.data.decode() or 'Portal' in response.data.decode()

    def test_login_email_incorrecto(self, client):
        """Test: Login con email que no existe."""
        response = client.post('/auth/login', data={
            'email': 'noexiste@test.com',
            'password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Email o contraseña incorrectos' in response.data.decode()

    def test_login_password_incorrecta(self, client, usuario_adoptante):
        """Test: Login con contraseña incorrecta."""
        response = client.post('/auth/login', data={
            'email': 'adoptante@test.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Email o contraseña incorrectos' in response.data.decode()

    def test_login_get_muestra_formulario(self, client):
        """Test: GET a /auth/login muestra el formulario."""
        response = client.get('/auth/login')

        assert response.status_code == 200
        assert 'Iniciar Sesión' in response.data.decode() or 'Login' in response.data.decode()
        assert 'email' in response.data.decode()
        assert 'password' in response.data.decode()


class TestLogout:
    """Tests para logout de usuarios."""

    def test_logout_exitoso(self, client, auth_headers_adoptante):
        """Test: Logout cierra sesión correctamente."""
        response = client.get('/auth/logout', follow_redirects=True)

        assert response.status_code == 200
        # Después del logout debería redirigir al inicio
        assert 'Iniciar Sesión' in response.data.decode() or 'Login' in response.data.decode()

    def test_logout_sin_autenticar(self, client):
        """Test: Logout sin estar autenticado redirige al login."""
        response = client.get('/auth/logout', follow_redirects=True)

        assert response.status_code == 200


class TestProteccionRutas:
    """Tests para verificar protección de rutas."""

    def test_ruta_protegida_sin_login(self, client):
        """Test: Acceso a ruta protegida sin login redirige."""
        response = client.get('/solicitudes/mis-solicitudes', follow_redirects=True)

        assert response.status_code == 200
        # Debe redirigir al login
        assert 'Iniciar Sesión' in response.data.decode() or 'Login' in response.data.decode()

    def test_admin_ruta_sin_permisos(self, client, auth_headers_adoptante):
        """Test: Adoptante no puede acceder a rutas de admin."""
        response = client.get('/mascotas/admin', follow_redirects=True)

        assert response.status_code == 200
        # Debe mostrar error de permisos o redirigir
        assert 'admin' in response.data.decode().lower() or 'permisos' in response.data.decode().lower()

    def test_admin_ruta_con_permisos(self, client, auth_headers_admin):
        """Test: Admin puede acceder a rutas de administración."""
        response = client.get('/mascotas/admin')

        assert response.status_code == 200
        assert 'admin' in response.data.decode().lower() or 'mascotas' in response.data.decode().lower()


class TestModelo:
    """Tests para el modelo Usuario."""

    def test_crear_usuario(self, app):
        """Test: Crear un usuario correctamente."""
        usuario = Usuario(
            email='modelo@test.com',
            nombre='Modelo Test',
            password='password123'
        )
        db.session.add(usuario)
        db.session.commit()

        # Verificar que se guardó
        usuario_bd = Usuario.query.filter_by(email='modelo@test.com').first()
        assert usuario_bd is not None
        assert usuario_bd.nombre == 'Modelo Test'
        assert usuario_bd.rol == 'adoptante'  # Por defecto

    def test_hash_password(self, app):
        """Test: La contraseña se hashea correctamente."""
        usuario = Usuario(
            email='hash@test.com',
            nombre='Hash Test',
            password='plaintext'
        )

        # El hash no debe ser igual al texto plano
        assert usuario.password_hash != 'plaintext'
        assert len(usuario.password_hash) > 20

    def test_check_password(self, app, usuario_adoptante):
        """Test: Verificación de contraseña funciona."""
        # Contraseña correcta
        assert usuario_adoptante.check_password('password123') is True

        # Contraseña incorrecta
        assert usuario_adoptante.check_password('wrongpassword') is False

    def test_is_admin(self, app):
        """Test: Método is_admin() funciona correctamente."""
        adoptante = Usuario(
            email='adoptante2@test.com',
            nombre='Adoptante',
            password='pass',
            rol='adoptante'
        )

        admin = Usuario(
            email='admin2@test.com',
            nombre='Admin',
            password='pass',
            rol='admin'
        )

        assert adoptante.is_admin() is False
        assert admin.is_admin() is True

    def test_repr_usuario(self, app, usuario_adoptante):
        """Test: Representación en string del usuario."""
        repr_str = repr(usuario_adoptante)

        assert 'Usuario' in repr_str
        assert 'adoptante@test.com' in repr_str
        assert 'adoptante' in repr_str
