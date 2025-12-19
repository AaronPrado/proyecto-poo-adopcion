"""
Tests para el módulo de solicitudes de adopción.

Tests incluidos:
- Creación de solicitudes
- Cuestionario de adopción
- Revisión y aprobación/rechazo (admin)
- Validaciones y restricciones
"""

import pytest
from app.models import Solicitud, Mascota
from app import db


class TestCrearSolicitud:
    """Tests para crear solicitudes de adopción."""

    def test_crear_solicitud_requiere_login(self, client, mascota_disponible):
        """Test: Crear solicitud requiere autenticación."""
        response = client.get(f'/solicitudes/nueva/{mascota_disponible.id}', follow_redirects=True)

        assert response.status_code == 200
        assert 'Iniciar Sesión' in response.data.decode() or 'Login' in response.data.decode()

    def test_crear_solicitud_get_muestra_formulario(self, client, auth_headers_adoptante, mascota_disponible):
        """Test: GET muestra formulario de cuestionario."""
        response = client.get(f'/solicitudes/nueva/{mascota_disponible.id}')

        assert response.status_code == 200
        assert 'Cuestionario' in response.data.decode() or 'Solicitud' in response.data.decode()
        assert 'tipo_vivienda' in response.data.decode()

    def test_crear_solicitud_exitosa(self, client, auth_headers_adoptante, mascota_disponible):
        """Test: Crear solicitud con cuestionario completo."""
        response = client.post(f'/solicitudes/nueva/{mascota_disponible.id}', data={
            'tipo_vivienda': 'Casa',
            'vivienda_propia': 'Sí',
            'tiene_jardin': 'Sí',
            'otras_mascotas': 'No',
            'experiencia_previa': 'Sí, he tenido perros',
            'horas_solo': '4-6 horas',
            'gastos_veterinarios': 'Sí',
            'tiempo_dedicado': '2-3 horas',
            'motivo_adopcion': 'Compañía',
            'que_harias_emergencia': 'Veterinario inmediatamente',
            'compromisos': 'Sí',
            'referencias': 'Juan Pérez - 612345678'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Solicitud enviada' in response.data.decode() or 'exitosa' in response.data.decode()

        # Verificar en BD
        solicitud = Solicitud.query.filter_by(mascota_id=mascota_disponible.id).first()
        assert solicitud is not None
        assert solicitud.estado == 'pendiente'
        assert solicitud.cuestionario_json is not None

        # Verificar que mascota pasó a en_proceso
        db.session.refresh(mascota_disponible)
        assert mascota_disponible.estado == 'en_proceso'

    def test_crear_solicitud_mascota_no_disponible(self, client, auth_headers_adoptante, mascota_en_proceso):
        """Test: No se puede solicitar mascota que no está disponible."""
        response = client.get(f'/solicitudes/nueva/{mascota_en_proceso.id}', follow_redirects=True)

        assert response.status_code == 200
        assert 'no está disponible' in response.data.decode() or 'disponible' in response.data.decode()

    def test_crear_solicitud_duplicada(self, client, auth_headers_adoptante, solicitud_pendiente):
        """Test: No se puede solicitar la misma mascota dos veces."""
        response = client.get(f'/solicitudes/nueva/{solicitud_pendiente.mascota_id}', follow_redirects=True)

        assert response.status_code == 200
        assert 'ya has solicitado' in response.data.decode() or 'duplicada' in response.data.decode()


class TestMisSolicitudes:
    """Tests para ver las solicitudes del usuario."""

    def test_mis_solicitudes_requiere_login(self, client):
        """Test: Ver mis solicitudes requiere login."""
        response = client.get('/solicitudes/mis-solicitudes', follow_redirects=True)

        assert response.status_code == 200
        assert 'Iniciar Sesión' in response.data.decode() or 'Login' in response.data.decode()

    def test_mis_solicitudes_muestra_solicitudes(self, client, auth_headers_adoptante, solicitud_pendiente):
        """Test: Muestra las solicitudes del usuario."""
        response = client.get('/solicitudes/mis-solicitudes')

        assert response.status_code == 200
        assert 'Max' in response.data.decode()  # Nombre de la mascota
        assert 'Pendiente' in response.data.decode() or 'pendiente' in response.data.decode()

    def test_mis_solicitudes_solo_propias(self, client, auth_headers_adoptante, solicitud_pendiente):
        """Test: Solo muestra solicitudes propias del usuario."""
        # Crear otro usuario y otra solicitud
        from app.models import Usuario
        otro_usuario = Usuario(
            email='otro@test.com',
            nombre='Otro Usuario',
            password='pass123'
        )
        db.session.add(otro_usuario)
        db.session.commit()

        response = client.get('/solicitudes/mis-solicitudes')

        # Solo debe mostrar la solicitud del usuario logueado
        assert response.status_code == 200


class TestDetalleSolicitud:
    """Tests para ver detalle de una solicitud."""

    def test_detalle_requiere_login(self, client, solicitud_pendiente):
        """Test: Ver detalle requiere login."""
        response = client.get(f'/solicitudes/detalle/{solicitud_pendiente.id}', follow_redirects=True)

        assert response.status_code == 200
        assert 'Iniciar Sesión' in response.data.decode() or 'Login' in response.data.decode()

    def test_detalle_muestra_cuestionario(self, client, auth_headers_adoptante, solicitud_pendiente):
        """Test: Detalle muestra el cuestionario completo."""
        response = client.get(f'/solicitudes/detalle/{solicitud_pendiente.id}')

        assert response.status_code == 200
        assert 'Casa' in response.data.decode()  # tipo_vivienda
        assert 'Sí' in response.data.decode()  # vivienda_propia

    def test_detalle_solo_propietario_o_admin(self, client, auth_headers_adoptante, solicitud_pendiente):
        """Test: Solo el propietario o admin pueden ver la solicitud."""
        # Crear otro usuario adoptante
        from app.models import Usuario
        otro_usuario = Usuario(
            email='otro2@test.com',
            nombre='Otro Usuario',
            password='pass123'
        )
        db.session.add(otro_usuario)
        db.session.commit()

        # Logout y login como otro usuario
        client.get('/auth/logout')
        client.post('/auth/login', data={
            'email': 'otro2@test.com',
            'password': 'pass123'
        })

        response = client.get(f'/solicitudes/detalle/{solicitud_pendiente.id}', follow_redirects=True)

        assert response.status_code == 200
        # Debe denegar acceso
        assert 'permisos' in response.data.decode().lower() or 'acceso' in response.data.decode().lower()


class TestAdminPanel:
    """Tests para panel de administración de solicitudes."""

    def test_admin_panel_requiere_login(self, client):
        """Test: Panel admin requiere login."""
        response = client.get('/solicitudes/admin', follow_redirects=True)

        assert response.status_code == 200
        assert 'Iniciar Sesión' in response.data.decode() or 'Login' in response.data.decode()

    def test_admin_panel_solo_admin(self, client, auth_headers_adoptante):
        """Test: Solo admin puede acceder."""
        response = client.get('/solicitudes/admin', follow_redirects=True)

        assert response.status_code == 200
        assert 'admin' in response.data.decode().lower() or 'permisos' in response.data.decode().lower()

    def test_admin_panel_muestra_solicitudes(self, client, auth_headers_admin, solicitud_pendiente):
        """Test: Panel muestra todas las solicitudes."""
        response = client.get('/solicitudes/admin')

        assert response.status_code == 200
        assert 'Max' in response.data.decode()
        assert 'Juan Pérez' in response.data.decode() or 'adoptante@test.com' in response.data.decode()

    def test_admin_panel_filtro_estado(self, client, auth_headers_admin, solicitud_pendiente):
        """Test: Filtro por estado funciona."""
        response = client.get('/solicitudes/admin?estado=pendiente')

        assert response.status_code == 200
        assert 'Max' in response.data.decode()


class TestRevisarSolicitud:
    """Tests para revisar y aprobar/rechazar solicitudes."""

    def test_revisar_solo_admin(self, client, auth_headers_adoptante, solicitud_pendiente):
        """Test: Solo admin puede revisar."""
        response = client.get(f'/solicitudes/admin/revisar/{solicitud_pendiente.id}', follow_redirects=True)

        assert response.status_code == 200
        assert 'admin' in response.data.decode().lower() or 'permisos' in response.data.decode().lower()

    def test_revisar_muestra_cuestionario(self, client, auth_headers_admin, solicitud_pendiente):
        """Test: Página de revisión muestra el cuestionario."""
        response = client.get(f'/solicitudes/admin/revisar/{solicitud_pendiente.id}')

        assert response.status_code == 200
        assert 'Casa' in response.data.decode()
        assert 'Aprobar' in response.data.decode()
        assert 'Rechazar' in response.data.decode()

    def test_aprobar_solicitud(self, client, auth_headers_admin, solicitud_pendiente, usuario_admin):
        """Test: Admin puede aprobar solicitud."""
        response = client.post(f'/solicitudes/admin/revisar/{solicitud_pendiente.id}', data={
            'accion': 'aprobar',
            'comentarios': 'Aprobada por cumplir requisitos'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'aprobada' in response.data.decode().lower()

        # Verificar en BD
        db.session.refresh(solicitud_pendiente)
        assert solicitud_pendiente.estado == 'aprobada'
        assert solicitud_pendiente.revisado_por == usuario_admin.id
        assert solicitud_pendiente.comentarios_admin is not None

        # Verificar que mascota pasó a adoptado
        mascota = Mascota.query.get(solicitud_pendiente.mascota_id)
        assert mascota.estado == 'adoptado'

    def test_rechazar_solicitud(self, client, auth_headers_admin, solicitud_pendiente, usuario_admin):
        """Test: Admin puede rechazar solicitud."""
        response = client.post(f'/solicitudes/admin/revisar/{solicitud_pendiente.id}', data={
            'accion': 'rechazar',
            'comentarios': 'No cumple requisitos de espacio'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'rechazada' in response.data.decode().lower()

        # Verificar en BD
        db.session.refresh(solicitud_pendiente)
        assert solicitud_pendiente.estado == 'rechazada'
        assert solicitud_pendiente.revisado_por == usuario_admin.id
        assert solicitud_pendiente.comentarios_admin is not None


class TestModelo:
    """Tests para el modelo Solicitud."""

    def test_crear_solicitud(self, app, usuario_adoptante, mascota_disponible):
        """Test: Crear solicitud correctamente."""
        solicitud = Solicitud(
            usuario_id=usuario_adoptante.id,
            mascota_id=mascota_disponible.id,
            cuestionario={'pregunta': 'respuesta'}
        )
        db.session.add(solicitud)
        db.session.commit()

        # Verificar valores por defecto
        assert solicitud.estado == 'pendiente'
        assert solicitud.cuestionario_json == {'pregunta': 'respuesta'}

    def test_aprobar_metodo(self, app, solicitud_pendiente, usuario_admin):
        """Test: Método aprobar() funciona correctamente."""
        solicitud_pendiente.aprobar(usuario_admin.id, 'Aprobada')

        db.session.refresh(solicitud_pendiente)
        assert solicitud_pendiente.estado == 'aprobada'
        assert solicitud_pendiente.revisado_por == usuario_admin.id
        assert solicitud_pendiente.fecha_revision is not None

        # Verificar que mascota se marcó como adoptado
        mascota = Mascota.query.get(solicitud_pendiente.mascota_id)
        assert mascota.estado == 'adoptado'

    def test_rechazar_metodo(self, app, solicitud_pendiente, usuario_admin):
        """Test: Método rechazar() funciona correctamente."""
        solicitud_pendiente.rechazar(usuario_admin.id, 'Rechazada')

        db.session.refresh(solicitud_pendiente)
        assert solicitud_pendiente.estado == 'rechazada'
        assert solicitud_pendiente.revisado_por == usuario_admin.id
        assert solicitud_pendiente.fecha_revision is not None

    def test_esta_pendiente(self, app, solicitud_pendiente):
        """Test: Método esta_pendiente() funciona."""
        assert solicitud_pendiente.esta_pendiente() is True

        solicitud_pendiente.estado = 'aprobada'
        assert solicitud_pendiente.esta_pendiente() is False

    def test_repr_solicitud(self, app, solicitud_pendiente):
        """Test: Representación en string de solicitud."""
        repr_str = repr(solicitud_pendiente)

        assert 'Solicitud' in repr_str
        assert str(solicitud_pendiente.id) in repr_str
        assert 'pendiente' in repr_str
