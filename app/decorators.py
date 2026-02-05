from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """
    Decorador que verifica si el usuario actual es administrador.
    Debe usarse DESPUÉS de @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('mascotas.catalogo'))
        return f(*args, **kwargs)
    return decorated_function