"""
Blueprint de rutas para la gestión de solicitudes de adopción.

Este módulo maneja:
- Creación de solicitudes con cuestionario (usuarios autenticados)
- Visualización de solicitudes del usuario
- Panel de administración para revisar solicitudes
- Aprobación/rechazo de solicitudes (solo admin)
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Solicitud, Mascota

# Crear blueprint
bp = Blueprint('solicitudes', __name__, url_prefix='/solicitudes')


@bp.route('/nueva/<int:mascota_id>', methods=['GET', 'POST'])
@login_required
def nueva(mascota_id):
    """
    Crear nueva solicitud de adopción con cuestionario.

    Muestra formulario con preguntas sobre el adoptante.
    Solo usuarios autenticados pueden solicitar.
    No se puede solicitar la misma mascota dos veces.

    Args:
        mascota_id (int): ID de la mascota a adoptar
    """
    mascota = Mascota.query.get_or_404(mascota_id)

    # Verificar que la mascota esté disponible
    if not mascota.esta_disponible():
        flash('Esta mascota ya no está disponible para adopción.', 'warning')
        return redirect(url_for('mascotas.detalle', mascota_id=mascota_id))

    # Verificar si el usuario ya tiene una solicitud para esta mascota
    solicitud_existente = Solicitud.query.filter_by(
        usuario_id=current_user.id,
        mascota_id=mascota_id
    ).first()

    if solicitud_existente:
        flash('Ya has enviado una solicitud para esta mascota.', 'info')
        return redirect(url_for('solicitudes.mis_solicitudes'))

    if request.method == 'POST':
        # Recoger respuestas del cuestionario
        cuestionario = {
            'vivienda_tipo': request.form.get('vivienda_tipo'),
            'vivienda_propia': request.form.get('vivienda_propia'),
            'tiene_jardin': request.form.get('tiene_jardin') == 'si',
            'tiene_mascotas': request.form.get('tiene_mascotas') == 'si',
            'mascotas_detalles': request.form.get('mascotas_detalles', ''),
            'experiencia_previa': request.form.get('experiencia_previa'),
            'horas_solo': request.form.get('horas_solo'),
            'motivo_adopcion': request.form.get('motivo_adopcion'),
            'compromiso_gastos': request.form.get('compromiso_gastos') == 'si',
            'compromiso_tiempo': request.form.get('compromiso_tiempo') == 'si',
            'emergencia_veterinaria': request.form.get('emergencia_veterinaria'),
            'referencias': request.form.get('referencias', '')
        }

        # Crear la solicitud
        solicitud = Solicitud(
            usuario_id=current_user.id,
            mascota_id=mascota_id,
            cuestionario=cuestionario
        )

        db.session.add(solicitud)

        # Marcar la mascota como "en proceso"
        mascota.marcar_en_proceso()

        db.session.commit()

        flash(f'¡Solicitud enviada con éxito para {mascota.nombre}! Revisaremos tu solicitud pronto.', 'success')
        return redirect(url_for('solicitudes.mis_solicitudes'))

    return render_template('solicitudes/nueva.html', mascota=mascota)


@bp.route('/mis-solicitudes')
@login_required
def mis_solicitudes():
    """
    Lista de solicitudes del usuario actual.

    Muestra todas las solicitudes creadas por el usuario
    con su estado actual (pendiente, aprobada, rechazada).
    """
    solicitudes = Solicitud.query.filter_by(usuario_id=current_user.id)\
        .order_by(Solicitud.fecha_solicitud.desc())\
        .all()

    return render_template('solicitudes/mis_solicitudes.html', solicitudes=solicitudes)


@bp.route('/detalle/<int:solicitud_id>')
@login_required
def detalle(solicitud_id):
    """
    Ver detalle de una solicitud específica.

    Muestra el cuestionario completo y el estado.
    Solo el usuario que creó la solicitud o admin pueden verla.

    Args:
        solicitud_id (int): ID de la solicitud
    """
    solicitud = Solicitud.query.get_or_404(solicitud_id)

    # Verificar permisos: solo el dueño o admin pueden ver
    if not current_user.is_admin() and solicitud.usuario_id != current_user.id:
        flash('No tienes permiso para ver esta solicitud.', 'danger')
        return redirect(url_for('solicitudes.mis_solicitudes'))

    return render_template('solicitudes/detalle.html', solicitud=solicitud)


# Rutas de ADMINISTRACIÓN
# Requieren autenticación y rol de admin

@bp.route('/admin')
@login_required
def admin_lista():
    """
    Panel de administración: lista de todas las solicitudes.

    Muestra todas las solicitudes con filtro por estado.
    Solo accesible para administradores.
    """
    # Verificar que el usuario sea admin
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('solicitudes.mis_solicitudes'))

    # Obtener filtro de estado si existe
    estado_filtro = request.args.get('estado', '')

    # Query base
    query = Solicitud.query

    # Aplicar filtro de estado si existe
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)

    # Ordenar por fecha (más recientes primero)
    solicitudes = query.order_by(Solicitud.fecha_solicitud.desc()).all()

    return render_template('solicitudes/admin/lista.html',
                         solicitudes=solicitudes,
                         estado_filtro=estado_filtro)


@bp.route('/admin/revisar/<int:solicitud_id>', methods=['GET', 'POST'])
@login_required
def admin_revisar(solicitud_id):
    """
    Revisar y aprobar/rechazar una solicitud.

    Muestra el detalle completo y permite al admin
    aprobar o rechazar con comentarios.
    Solo accesible para administradores.

    Args:
        solicitud_id (int): ID de la solicitud
    """
    # Verificar que el usuario sea admin
    if not current_user.is_admin():
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('solicitudes.mis_solicitudes'))

    solicitud = Solicitud.query.get_or_404(solicitud_id)

    if request.method == 'POST':
        accion = request.form.get('accion')
        comentarios = request.form.get('comentarios', '')

        if accion == 'aprobar':
            solicitud.aprobar(current_user.id, comentarios)
            flash(f'Solicitud aprobada. {solicitud.usuario.nombre} ha adoptado a {solicitud.mascota.nombre}.', 'success')
        elif accion == 'rechazar':
            solicitud.rechazar(current_user.id, comentarios)
            flash(f'Solicitud rechazada.', 'info')

        return redirect(url_for('solicitudes.admin_lista'))

    return render_template('solicitudes/admin/revisar.html', solicitud=solicitud)