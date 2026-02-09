"""
Tests para la API REST.

Tests incluidos:
- Autenticación JWT (login)
- Endpoints de mascotas (listar, detalle, filtros)
- Endpoints de solicitudes (crear, listar)
"""

import pytest
import json
from app.models import Usuario, Mascota, Solicitud


class TestAuthAPI:
    """Tests para /api/auth"""

    def test_login_exitoso(self, client, usuario_adoptante):
        """POST /api/auth/login con credenciales válidas."""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'email': 'adoptante@test.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert 'user' in data
        assert data['user']['email'] == 'adoptante@test.com'

    def test_login_credenciales_invalidas(self, client, usuario_adoptante):
        """POST /api/auth/login con password incorrecto."""
        response = client.post('/api/auth/login',
            data=json.dumps({
                'email': 'adoptante@test.com',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_login_sin_datos(self, client):
        """POST /api/auth/login sin body."""
        response = client.post('/api/auth/login',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400


class TestMascotasAPI:
    """Tests para /api/mascotas"""

    def test_listar_mascotas(self, client, mascota_disponible):
        """GET /api/mascotas/ devuelve lista de mascotas."""
        response = client.get('/api/mascotas/')

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]['nombre'] == 'Cerbero'

    def test_listar_mascotas_filtro_especie(self, client, mascota_disponible):
        """GET /api/mascotas/?especie=Perro filtra correctamente."""
        response = client.get('/api/mascotas/?especie=Perro')

        assert response.status_code == 200
        data = response.get_json()
        assert all(m['especie'] == 'Perro' for m in data)

    def test_detalle_mascota(self, client, mascota_disponible):
        """GET /api/mascotas/<id> devuelve detalle."""
        response = client.get(f'/api/mascotas/{mascota_disponible.id}')

        assert response.status_code == 200
        data = response.get_json()
        assert data['nombre'] == 'Cerbero'
        assert data['id'] == mascota_disponible.id

    def test_detalle_mascota_no_existe(self, client):
        """GET /api/mascotas/999 devuelve 404."""
        response = client.get('/api/mascotas/999')

        assert response.status_code == 404


class TestSolicitudesAPI:
    """Tests para /api/solicitudes"""

    def get_token(self, client, email='adoptante@test.com', password='password123'):
        """Helper para obtener token JWT."""
        response = client.post('/api/auth/login',
            data=json.dumps({'email': email, 'password': password}),
            content_type='application/json'
        )
        return response.get_json()['token']

    def test_mis_solicitudes_sin_token(self, client):
        """GET /api/solicitudes/mias sin JWT devuelve 401."""
        response = client.get('/api/solicitudes/mias')

        assert response.status_code == 401

    def test_mis_solicitudes_con_token(self, client, usuario_adoptante):
        """GET /api/solicitudes/mias con JWT devuelve lista."""
        token = self.get_token(client)

        response = client.get('/api/solicitudes/mias',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)

    def test_crear_solicitud_exitosa(self, client, usuario_adoptante, mascota_disponible):
        """POST /api/solicitudes/ crea solicitud."""
        token = self.get_token(client)

        response = client.post('/api/solicitudes/',
            data=json.dumps({
                'mascota_id': mascota_disponible.id,
                'cuestionario': {
                    'vivienda_tipo': 'Casa',
                    'tiene_jardin': True,
                    'experiencia_previa': True
                }
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['mascota_id'] == mascota_disponible.id
        assert data['estado'] == 'pendiente'

    def test_crear_solicitud_sin_token(self, client, mascota_disponible):
        """POST /api/solicitudes/ sin JWT devuelve 401."""
        response = client.post('/api/solicitudes/',
            data=json.dumps({
                'mascota_id': mascota_disponible.id,
                'cuestionario': {}
            }),
            content_type='application/json'
        )

        assert response.status_code == 401

    def test_crear_solicitud_mascota_no_existe(self, client, usuario_adoptante):
        """POST /api/solicitudes/ con mascota inexistente devuelve 404."""
        token = self.get_token(client)

        response = client.post('/api/solicitudes/',
            data=json.dumps({
                'mascota_id': 999,
                'cuestionario': {'test': 'data'}
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 404

    def test_crear_solicitud_mascota_no_disponible(self, client, usuario_adoptante, mascota_en_proceso):
        """POST /api/solicitudes/ con mascota en proceso devuelve 400."""
        token = self.get_token(client)

        response = client.post('/api/solicitudes/',
            data=json.dumps({
                'mascota_id': mascota_en_proceso.id,
                'cuestionario': {'test': 'data'}
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 400
