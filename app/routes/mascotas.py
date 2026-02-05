"""
Blueprint de rutas para la gestión de mascotas.

Este módulo maneja:
- Catálogo público de mascotas disponibles (sin autenticación)
- Vista detalle de cada mascota
- Panel de administración con CRUD completo (solo admin)
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Mascota
from app.decorators import admin_required

# Crear blueprint
bp = Blueprint('mascotas', __name__, url_prefix='/mascotas')


@bp.route('/')
@bp.route('/catalogo')
def catalogo():
    """
    Catálogo público de mascotas disponibles.

    Muestra todas las mascotas en estado 'disponible'.
    Permite filtrar por especie, tamaño, sexo y edad.
    Accesible sin autenticación.
    """
    # Obtener parámetros de filtrado
    especie_filtro = request.args.get('especie', '')
    tamano_filtro = request.args.get('tamano', '')
    sexo_filtro = request.args.get('sexo', '')
    edad_filtro = request.args.get('edad', '')

    # Query base: solo mascotas disponibles
    query = Mascota.query.filter_by(estado='disponible')

    # Aplicar filtros si existen
    if especie_filtro:
        query = query.filter(Mascota.especie == especie_filtro)

    if tamano_filtro:
        query = query.filter(Mascota.tamano == tamano_filtro)

    if sexo_filtro:
        query = query.filter(Mascota.sexo == sexo_filtro)

    if edad_filtro:
        try:
            edad_max = int(edad_filtro)
            query = query.filter(Mascota.edad_aprox <= edad_max)
        except ValueError:
            pass  # Ignorar si el filtro de edad no es válido

    # Ordenar por fecha de ingreso (más recientes primero)
    mascotas = query.order_by(Mascota.fecha_ingreso.desc()).all()

    # Obtener lista de especies únicas disponibles
    especies_disponibles = db.session.query(Mascota.especie)\
        .filter_by(estado='disponible')\
        .distinct()\
        .order_by(Mascota.especie)\
        .all()
    especies_disponibles = [esp[0] for esp in especies_disponibles if esp[0]]

    return render_template('mascotas/catalogo.html',
                         mascotas=mascotas,
                         especies_disponibles=especies_disponibles,
                         especie_filtro=especie_filtro,
                         tamano_filtro=tamano_filtro,
                         sexo_filtro=sexo_filtro,
                         edad_filtro=edad_filtro)


@bp.route('/<int:mascota_id>')
def detalle(mascota_id):
    """
    Vista detalle de una mascota específica.

    Muestra toda la información de la mascota.
    Accesible sin autenticación.

    Args:
        mascota_id (int): ID de la mascota
    """
    mascota = Mascota.query.get_or_404(mascota_id)
    return render_template('mascotas/detalle.html', mascota=mascota)


# ==================== RUTAS DE ADMINISTRACIÓN ====================
# Requieren autenticación y rol de admin

@bp.route('/admin')
@login_required
@admin_required
def admin_lista():
    """
    Panel de administración: lista de todas las mascotas.

    Muestra todas las mascotas (disponibles, en proceso, adoptadas).
    Solo accesible para administradores.
    Permite ordenar por cualquier columna.
    """

    # Obtener parámetros de URL
    estado_filtro = request.args.get('estado', '')
    orden_campo = request.args.get('orden', 'id')  # Campo por el cual ordenar
    orden_dir = request.args.get('dir', 'asc')  # Dirección: asc o desc

    # Query base
    query = Mascota.query

    # Aplicar filtro de estado si existe
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)

    # Mapeo de nombres de columnas a atributos del modelo
    columnas_validas = {
        'id': Mascota.id,
        'nombre': Mascota.nombre,
        'especie': Mascota.especie,
        'raza': Mascota.raza,
        'edad': Mascota.edad_aprox,
        'tamano': Mascota.tamano,
        'estado': Mascota.estado
    }

    # Aplicar ordenamiento
    if orden_campo in columnas_validas:
        columna = columnas_validas[orden_campo]
        if orden_dir == 'desc':
            query = query.order_by(columna.desc())
        else:
            query = query.order_by(columna.asc())
    else:
        # Orden por defecto
        query = query.order_by(Mascota.id.asc())

    mascotas = query.all()

    return render_template('mascotas/admin/lista.html',
                         mascotas=mascotas,
                         estado_filtro=estado_filtro,
                         orden_campo=orden_campo,
                         orden_dir=orden_dir)


@bp.route('/admin/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_nueva():
    """
    Crear una nueva mascota.

    GET: Muestra formulario de creación
    POST: Procesa y guarda la nueva mascota
    Solo accesible para administradores.
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        especie = request.form.get('especie', '').strip()
        raza = request.form.get('raza', '').strip()
        edad_aprox = request.form.get('edad_aprox', '')
        sexo = request.form.get('sexo', '').strip()
        tamano = request.form.get('tamano', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        foto_url = request.form.get('foto_url', '').strip()
        vacunado = request.form.get('vacunado') == 'on'
        esterilizado = request.form.get('esterilizado') == 'on'

        # Validaciones básicas
        if not nombre or len(nombre) < 2:
            flash('El nombre debe tener al menos 2 caracteres.', 'danger')
            return render_template('mascotas/admin/form.html', mascota=None)

        if not especie or len(especie) < 2:
            flash('La especie es obligatoria.', 'danger')
            return render_template('mascotas/admin/form.html', mascota=None)

        if not descripcion or len(descripcion) < 10:
            flash('La descripción debe tener al menos 10 caracteres.', 'danger')
            return render_template('mascotas/admin/form.html', mascota=None)

        # Convertir edad a entero
        try:
            edad_aprox = int(edad_aprox) if edad_aprox else None
            if edad_aprox is not None and (edad_aprox < 0 or edad_aprox > 30):
                flash('La edad debe estar entre 0 y 30 años.', 'danger')
                return render_template('mascotas/admin/form.html', mascota=None)
        except ValueError:
            flash('La edad debe ser un número válido.', 'danger')
            return render_template('mascotas/admin/form.html', mascota=None)

        # Crear nueva mascota
        nueva_mascota = Mascota(
            nombre=nombre,
            especie=especie,
            descripcion=descripcion,
            raza=raza if raza else None,
            edad_aprox=edad_aprox,
            sexo=sexo if sexo else None,
            tamano=tamano if tamano else None,
            foto_url=foto_url if foto_url else None,
            vacunado=vacunado,
            esterilizado=esterilizado,
            estado='disponible'
        )

        try:
            db.session.add(nueva_mascota)
            db.session.commit()
            flash(f'Mascota "{nombre}" creada exitosamente.', 'success')
            return redirect(url_for('mascotas.admin_lista'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la mascota: {str(e)}', 'danger')
            return render_template('mascotas/admin/form.html', mascota=None)

    # GET: Mostrar formulario vacío
    return render_template('mascotas/admin/form.html', mascota=None)


@bp.route('/admin/editar/<int:mascota_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_editar(mascota_id):
    """
    Editar una mascota existente.

    GET: Muestra formulario con datos actuales
    POST: Procesa y guarda los cambios
    Solo accesible para administradores.

    Args:
        mascota_id (int): ID de la mascota a editar
    """

    # Obtener la mascota
    mascota = Mascota.query.get_or_404(mascota_id)

    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        especie = request.form.get('especie', '').strip()
        raza = request.form.get('raza', '').strip()
        edad_aprox = request.form.get('edad_aprox', '')
        sexo = request.form.get('sexo', '').strip()
        tamano = request.form.get('tamano', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        foto_url = request.form.get('foto_url', '').strip()
        estado = request.form.get('estado', '').strip()
        vacunado = request.form.get('vacunado') == 'on'
        esterilizado = request.form.get('esterilizado') == 'on'

        # Validaciones básicas
        if not nombre or len(nombre) < 2:
            flash('El nombre debe tener al menos 2 caracteres.', 'danger')
            return render_template('mascotas/admin/form.html', mascota=mascota)

        if not especie or len(especie) < 2:
            flash('La especie es obligatoria.', 'danger')
            return render_template('mascotas/admin/form.html', mascota=mascota)

        if not descripcion or len(descripcion) < 10:
            flash('La descripción debe tener al menos 10 caracteres.', 'danger')
            return render_template('mascotas/admin/form.html', mascota=mascota)

        # Convertir edad a entero
        try:
            edad_aprox = int(edad_aprox) if edad_aprox else None
            if edad_aprox is not None and (edad_aprox < 0 or edad_aprox > 30):
                flash('La edad debe estar entre 0 y 30 años.', 'danger')
                return render_template('mascotas/admin/form.html', mascota=mascota)
        except ValueError:
            flash('La edad debe ser un número válido.', 'danger')
            return render_template('mascotas/admin/form.html', mascota=mascota)

        # Actualizar datos
        mascota.nombre = nombre
        mascota.especie = especie
        mascota.raza = raza if raza else None
        mascota.edad_aprox = edad_aprox
        mascota.sexo = sexo if sexo else None
        mascota.tamano = tamano if tamano else None
        mascota.descripcion = descripcion
        mascota.foto_url = foto_url if foto_url else None
        mascota.estado = estado if estado in ['disponible', 'en_proceso', 'adoptado'] else 'disponible'
        mascota.vacunado = vacunado
        mascota.esterilizado = esterilizado

        try:
            db.session.commit()
            flash(f'Mascota "{nombre}" actualizada exitosamente.', 'success')
            return redirect(url_for('mascotas.admin_lista'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la mascota: {str(e)}', 'danger')
            return render_template('mascotas/admin/form.html', mascota=mascota)

    # GET: Mostrar formulario con datos actuales
    return render_template('mascotas/admin/form.html', mascota=mascota)


@bp.route('/admin/eliminar/<int:mascota_id>', methods=['POST'])
@login_required
@admin_required
def admin_eliminar(mascota_id):
    """
    Eliminar una mascota.

    Solo accesible para administradores.
    Solo se permite eliminar si no tiene solicitudes asociadas.

    Args:
        mascota_id (int): ID de la mascota a eliminar
    """

    # Obtener la mascota
    mascota = Mascota.query.get_or_404(mascota_id)

    # Verificar si tiene solicitudes asociadas
    if mascota.solicitudes.count() > 0:
        flash(f'No se puede eliminar "{mascota.nombre}" porque tiene solicitudes de adopción asociadas.', 'danger')
        return redirect(url_for('mascotas.admin_lista'))

    try:
        nombre = mascota.nombre
        db.session.delete(mascota)
        db.session.commit()
        flash(f'Mascota "{nombre}" eliminada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la mascota: {str(e)}', 'danger')

    return redirect(url_for('mascotas.admin_lista'))
