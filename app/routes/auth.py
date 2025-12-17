"""
Blueprint de autenticación: registro, login, logout.

Este módulo maneja todas las rutas relacionadas con la autenticación
de usuarios en el sistema.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import db
from app.models import Usuario

# Crear blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Ruta de registro de nuevos usuarios.
    
    GET: Muestra el formulario de registro
    POST: Procesa el registro y crea el usuario
    
    Returns:
        Template renderizado o redirección
    """
    # Si el usuario ya está autenticado, redirigir al inicio
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Obtener datos del formulario
        email = request.form.get('email', '').strip().lower()
        nombre = request.form.get('nombre', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        telefono = request.form.get('telefono', '').strip()
        direccion = request.form.get('direccion', '').strip()
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validaciones
        if not email or not nombre or not password:
            flash('Email, nombre y contraseña son obligatorios.', 'danger')
            return render_template('auth/registro.html')
        
        if password != password_confirm:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('auth/registro.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'danger')
            return render_template('auth/registro.html')
        
        # Verificar si el email ya existe
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado. Intenta iniciar sesión.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Crear nuevo usuario
        try:
            nuevo_usuario = Usuario(
                email=email,
                nombre=nombre,
                password=password,
                rol='adoptante'  # Por defecto todos son adoptantes
            )
            nuevo_usuario.apellidos = apellidos
            nuevo_usuario.telefono = telefono
            nuevo_usuario.direccion = direccion
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'danger')
            return render_template('auth/registro.html')
    
    # GET: Mostrar formulario
    return render_template('auth/registro.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta de inicio de sesión.
    
    GET: Muestra el formulario de login
    POST: Autentica al usuario
    
    Returns:
        Template renderizado o redirección
    """
    # Si el usuario ya está autenticado, redirigir al inicio
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        remember = request.form.get('remember', False)  # Checkbox "Recordarme"
        
        # Validaciones básicas
        if not email or not password:
            flash('Email y contraseña son obligatorios.', 'danger')
            return render_template('auth/login.html')
        
        # Buscar usuario por email
        usuario = Usuario.query.filter_by(email=email).first()
        
        # Verificar credenciales
        if usuario is None or not usuario.check_password(password):
            flash('Email o contraseña incorrectos.', 'danger')
            return render_template('auth/login.html')
        
        # Verificar si la cuenta está activa
        if not usuario.activo:
            flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'warning')
            return render_template('auth/login.html')
        
        # Login exitoso
        login_user(usuario, remember=remember)
        flash(f'¡Bienvenido, {usuario.nombre}!', 'success')
        
        # Redirigir a la página que intentaba acceder o al inicio
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        else:
            return redirect(url_for('index'))
    
    # GET: Mostrar formulario
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """
    Ruta de cierre de sesión.
    
    Cierra la sesión del usuario actual y redirige al inicio.
    
    Returns:
        Redirección a la página de inicio
    """
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('index'))
