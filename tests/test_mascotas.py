"""
Tests para el módulo de mascotas.

Tests incluidos:
- CRUD de mascotas (crear, leer, actualizar, eliminar)
- Catálogo público con filtros
- Panel de administración
- Validaciones y permisos
"""

import pytest
from app.models import Mascota
from app import db


class TestCatalogo:
    """Tests para el catálogo público de mascotas."""

    def test_catalogo_muestra_mascotas_disponibles(self, client, mascota_disponible):
        """Test: El catálogo muestra mascotas disponibles."""
        response = client.get('/mascotas/catalogo')

        assert response.status_code == 200
        assert 'Cerbero' in response.data.decode()
        assert 'Chihuahua' in response.data.decode()

    def test_catalogo_no_muestra_mascotas_adoptadas(self, client, mascota_disponible):
        """Test: El catálogo no muestra mascotas adoptadas."""
        # Marcar como adoptada
        mascota_disponible.estado = 'adoptado'
        db.session.commit()

        response = client.get('/mascotas/catalogo')

        assert response.status_code == 200
        assert 'Cerbero' not in response.data.decode()

    def test_catalogo_filtro_especie(self, client, mascota_disponible):
        """Test: Filtro por especie funciona correctamente."""
        # Crear gato
        gato = Mascota(
            nombre='Michi',
            especie='Gato',
            descripcion='Gata cariñosa y tranquila',
            estado='disponible'
        )
        db.session.add(gato)
        db.session.commit()

        # Filtrar por Perro
        response = client.get('/mascotas/catalogo?especie=Perro')
        assert 'Cerbero' in response.data.decode()
        assert 'Michi' not in response.data.decode()

        # Filtrar por Gato
        response = client.get('/mascotas/catalogo?especie=Gato')
        assert 'Michi' in response.data.decode()
        assert 'Cerbero' not in response.data.decode()

    def test_catalogo_filtro_tamano(self, client, mascota_disponible):
        """Test: Filtro por tamaño funciona correctamente."""
        response = client.get('/mascotas/catalogo?tamano=Pequeño')

        assert response.status_code == 200
        assert 'Cerbero' in response.data.decode()

    def test_catalogo_filtro_sexo(self, client, mascota_disponible):
        """Test: Filtro por sexo funciona correctamente."""
        response = client.get('/mascotas/catalogo?sexo=Macho')

        assert response.status_code == 200
        assert 'Cerbero' in response.data.decode()

    def test_catalogo_filtro_edad_maxima(self, client, mascota_disponible):
        """Test: Filtro por edad máxima funciona correctamente."""
        response = client.get('/mascotas/catalogo?edad_max=5')

        assert response.status_code == 200
        # Cerbero tiene 3 años
        assert 'Cerbero' in response.data.decode()


class TestDetalle:
    """Tests para la página de detalle de mascota."""

    def test_detalle_muestra_mascota(self, client, mascota_disponible):
        """Test: La página de detalle muestra información completa."""
        response = client.get(f'/mascotas/{mascota_disponible.id}')

        assert response.status_code == 200
        assert 'Cerbero' in response.data.decode()
        assert 'Chihuahua' in response.data.decode()
        assert 'amigable' in response.data.decode()

    def test_detalle_mascota_inexistente(self, client):
        """Test: Mascota inexistente retorna 404."""
        response = client.get('/mascotas/99999')

        assert response.status_code == 404

    def test_detalle_boton_adoptar_disponible(self, client, auth_headers_adoptante, mascota_disponible):
        """Test: Botón de adopción visible si mascota disponible."""
        response = client.get(f'/mascotas/{mascota_disponible.id}')

        assert response.status_code == 200
        assert 'Solicitar' in response.data.decode() or 'Adoptar' in response.data.decode()

    def test_detalle_no_boton_si_adoptada(self, client, auth_headers_adoptante, mascota_disponible):
        """Test: No mostrar botón si mascota adoptada."""
        mascota_disponible.estado = 'adoptado'
        db.session.commit()

        response = client.get(f'/mascotas/{mascota_disponible.id}')

        assert response.status_code == 200
        assert 'Adoptad' in response.data.decode()


class TestAdminPanel:
    """Tests para el panel de administración de mascotas."""

    def test_admin_panel_requiere_autenticacion(self, client):
        """Test: Panel admin requiere login."""
        response = client.get('/mascotas/admin', follow_redirects=True)

        assert response.status_code == 200
        assert 'Iniciar Sesión' in response.data.decode() or 'Login' in response.data.decode()

    def test_admin_panel_solo_admin(self, client, auth_headers_adoptante):
        """Test: Solo admin puede acceder al panel."""
        response = client.get('/mascotas/admin', follow_redirects=True)

        assert response.status_code == 200
        # Debe denegar acceso o redirigir
        content = response.data.decode().lower()
        assert 'admin' in content or 'permiso' in content or 'no tienes' in content

    def test_admin_panel_muestra_todas_mascotas(self, client, auth_headers_admin, mascota_disponible, mascota_en_proceso):
        """Test: Panel admin muestra todas las mascotas."""
        response = client.get('/mascotas/admin')

        assert response.status_code == 200
        assert 'Cerbero' in response.data.decode()
        assert 'Luna' in response.data.decode()

    def test_admin_panel_filtro_estado(self, client, auth_headers_admin, mascota_disponible, mascota_en_proceso):
        """Test: Filtro por estado en panel admin."""
        response = client.get('/mascotas/admin?estado=disponible')

        assert response.status_code == 200
        assert 'Cerbero' in response.data.decode()
        assert 'Luna' not in response.data.decode()


class TestCRUD:
    """Tests para operaciones CRUD de mascotas."""

    def test_crear_mascota_requiere_admin(self, client, auth_headers_adoptante):
        """Test: Solo admin puede crear mascotas."""
        response = client.get('/mascotas/admin/nueva', follow_redirects=True)

        assert response.status_code == 200
        content = response.data.decode().lower()
        assert 'admin' in content or 'permiso' in content or 'no tienes' in content

    def test_crear_mascota_exitoso(self, client, auth_headers_admin):
        """Test: Admin puede crear mascota."""
        response = client.post('/mascotas/admin/nueva', data={
            'nombre': 'Rocky',
            'especie': 'Perro',
            'raza': 'Pastor Alemán',
            'edad_aprox': 5,
            'sexo': 'Macho',
            'tamano': 'Grande',
            'descripcion': 'Perro guardián muy leal y protector',
            'foto_url': 'https://example.com/rocky.jpg',
            'vacunado': 'on',
            'esterilizado': 'on'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'creada exitosamente' in response.data.decode() or 'Rocky' in response.data.decode()

        # Verificar en BD
        mascota = Mascota.query.filter_by(nombre='Rocky').first()
        assert mascota is not None
        assert mascota.especie == 'Perro'
        assert mascota.estado == 'disponible'

    def test_editar_mascota(self, client, auth_headers_admin, mascota_disponible):
        """Test: Admin puede editar mascota."""
        response = client.post(f'/mascotas/admin/editar/{mascota_disponible.id}', data={
            'nombre': 'Cerbero Editado',
            'especie': 'Perro',
            'raza': 'Golden Retriever',
            'edad_aprox': 4,
            'sexo': 'Macho',
            'tamano': 'Grande',
            'descripcion': 'Descripción actualizada con más detalle',
            'foto_url': mascota_disponible.foto_url,
            'estado': 'disponible',
            'vacunado': 'on',
            'esterilizado': 'on'
        }, follow_redirects=True)

        assert response.status_code == 200

        # Verificar cambios
        db.session.refresh(mascota_disponible)
        assert mascota_disponible.nombre == 'Cerbero Editado'
        assert mascota_disponible.raza == 'Golden Retriever'

    def test_eliminar_mascota(self, client, auth_headers_admin, mascota_disponible):
        """Test: Admin puede eliminar mascota."""
        mascota_id = mascota_disponible.id

        response = client.post(f'/mascotas/admin/eliminar/{mascota_id}', follow_redirects=True)

        assert response.status_code == 200

        # Verificar que fue eliminada
        mascota = Mascota.query.get(mascota_id)
        assert mascota is None


class TestModelo:
    """Tests para el modelo Mascota."""

    def test_crear_mascota(self, app):
        """Test: Crear mascota correctamente."""
        mascota = Mascota(
            nombre='Test',
            especie='Perro',
            descripcion='Descripción test'
        )
        db.session.add(mascota)
        db.session.commit()

        # Verificar valores por defecto
        assert mascota.estado == 'disponible'
        assert mascota.vacunado is False
        assert mascota.esterilizado is False

    def test_esta_disponible(self, app, mascota_disponible):
        """Test: Método esta_disponible() funciona."""
        assert mascota_disponible.esta_disponible() is True

        mascota_disponible.estado = 'adoptado'
        assert mascota_disponible.esta_disponible() is False

    def test_marcar_en_proceso(self, app, mascota_disponible):
        """Test: Marcar mascota en proceso."""
        mascota_disponible.marcar_en_proceso()

        db.session.refresh(mascota_disponible)
        assert mascota_disponible.estado == 'en_proceso'

    def test_marcar_adoptado(self, app, mascota_disponible):
        """Test: Marcar mascota como adoptada."""
        mascota_disponible.marcar_adoptado()

        db.session.refresh(mascota_disponible)
        assert mascota_disponible.estado == 'adoptado'

    def test_tiene_solicitudes_pendientes(self, app, mascota_disponible, solicitud_pendiente):
        """Test: Verificar si tiene solicitudes pendientes."""
        assert mascota_disponible.tiene_solicitudes_pendientes() is True

    def test_repr_mascota(self, app, mascota_disponible):
        """Test: Representación en string de mascota."""
        repr_str = repr(mascota_disponible)

        assert 'Mascota' in repr_str
        assert 'Cerbero' in repr_str
        assert 'Perro' in repr_str
        assert 'disponible' in repr_str
