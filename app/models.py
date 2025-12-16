"""
Modelos de la base de datos usando SQLAlchemy.
Representa las entidades: Usuario, Mascota, Solicitud.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# Instancia de SQLAlchemy
db = SQLAlchemy()


class Usuario(db.Model):
    """
    Modelo de Usuario del sistema.

    Representa tanto a adoptantes como administradores del refugio.
    Los usuarios pueden crear solicitudes de adopción (adoptantes)
    o revisarlas (administradores).

    Attributes:
        id (int): Identificador único del usuario
        email (str): Email único para login
        password_hash (str): Contraseña hasheada con bcrypt
        nombre (str): Nombre completo del usuario
        telefono (str): Teléfono de contacto (opcional)
        direccion (str): Dirección completa (opcional)
        rol (str): 'adoptante' o 'admin'
        fecha_registro (datetime): Fecha de creación de la cuenta
        activo (bool): Si la cuenta está activa
        solicitudes (relationship): Solicitudes creadas por el usuario
        solicitudes_revisadas (relationship): Solicitudes revisadas (solo admin)
    """

    __tablename__ = 'usuarios'

    # Atributos de la tabla
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    rol = db.Column(db.String(20), nullable=False, default='adoptante', index=True)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    # Relaciones
    solicitudes = db.relationship(
        'Solicitud',
        foreign_keys='Solicitud.usuario_id',
        backref='usuario',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    solicitudes_revisadas = db.relationship(
        'Solicitud',
        foreign_keys='Solicitud.revisado_por',
        backref='revisor',
        lazy='dynamic'
    )

    def __init__(self, email, nombre, password, rol='adoptante'):
        """
        Constructor del Usuario.

        Args:
            email (str): Email del usuario
            nombre (str): Nombre completo
            password (str): Contraseña en texto plano (se hasheará)
            rol (str): 'adoptante' o 'admin' (por defecto 'adoptante')
        """
        self.email = email
        self.nombre = nombre
        self.set_password(password)
        self.rol = rol

    def set_password(self, password):
        """
        Hashea y guarda la contraseña.

        Args:
            password (str): Contraseña en texto plano
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifica si la contraseña es correcta.

        Args:
            password (str): Contraseña a verificar

        Returns:
            bool: True si es correcta, False si no
        """
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """
        Comprueba si el usuario es administrador.

        Returns:
            bool: True si es admin, False si es adoptante
        """
        return self.rol == 'admin'

    def __repr__(self):
        """Representación en string del objeto."""
        return f'<Usuario {self.email} ({self.rol})>'


class Mascota(db.Model):
    """
    Modelo de Mascota disponible para adopción.

    Representa un animal del refugio que puede ser adoptado.
    Contiene información sobre sus características, estado
    y relación con las solicitudes de adopción.

    Attributes:
        id (int): Identificador único de la mascota
        nombre (str): Nombre de la mascota
        especie (str): Tipo de animal (Perro, Gato, etc.)
        raza (str): Raza específica o 'Mestizo'
        edad_aprox (int): Edad aproximada en años
        sexo (str): 'Macho', 'Hembra', 'Desconocido'
        tamano (str): 'Pequeño', 'Mediano', 'Grande'
        descripcion (str): Historia y personalidad
        estado (str): 'disponible', 'en_proceso', 'adoptado'
        foto_url (str): Ruta a la imagen
        fecha_ingreso (datetime): Cuándo llegó al refugio
        vacunado (bool): Si está vacunado
        esterilizado (bool): Si está esterilizado
        solicitudes (relationship): Solicitudes para esta mascota
    """

    __tablename__ = 'mascotas'

    # Atributos de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False, index=True)
    raza = db.Column(db.String(100))
    edad_aprox = db.Column(db.Integer)
    sexo = db.Column(db.String(10))
    tamano = db.Column(db.String(20))
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default='disponible', index=True)
    foto_url = db.Column(db.String(255))
    fecha_ingreso = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    vacunado = db.Column(db.Boolean, nullable=False, default=False)
    esterilizado = db.Column(db.Boolean, nullable=False, default=False)

    # Relaciones
    solicitudes = db.relationship(
        'Solicitud',
        backref='mascota',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __init__(self, nombre, especie, descripcion, **kwargs):
        """
        Constructor de Mascota.

        Args:
            nombre (str): Nombre de la mascota
            especie (str): Tipo de animal
            descripcion (str): Descripción completa
            **kwargs: Otros atributos opcionales (raza, edad, sexo, etc.)
        """
        self.nombre = nombre
        self.especie = especie
        self.descripcion = descripcion

        # Atributos opcionales
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def esta_disponible(self):
        """
        Verifica si la mascota está disponible para adopción.

        Returns:
            bool: True si está disponible, False si no
        """
        return self.estado == 'disponible'

    def marcar_en_proceso(self):
        """Marca la mascota como 'en proceso' de adopción."""
        self.estado = 'en_proceso'
        db.session.commit()

    def marcar_adoptado(self):
        """Marca la mascota como adoptada."""
        self.estado = 'adoptado'
        db.session.commit()

    def tiene_solicitudes_pendientes(self):
        """
        Verifica si tiene solicitudes pendientes de revisión.

        Returns:
            bool: True si tiene solicitudes pendientes
        """
        return self.solicitudes.filter_by(estado='pendiente').count() > 0

    def __repr__(self):
        """Representación en string del objeto."""
        return f'<Mascota {self.nombre} ({self.especie}) - {self.estado}>'


class Solicitud(db.Model):
    """
    Modelo de Solicitud de Adopción.

    Representa una petición de adopción realizada por un usuario
    para una mascota específica. Contiene el cuestionario respondido
    y el estado de revisión.

    Attributes:
        id (int): Identificador único de la solicitud
        usuario_id (int): ID del usuario que solicita
        mascota_id (int): ID de la mascota solicitada
        fecha_solicitud (datetime): Cuándo se creó
        estado (str): 'pendiente', 'aprobada', 'rechazada'
        cuestionario_json (dict): Respuestas en formato JSON
        comentarios_admin (str): Feedback del administrador
        fecha_revision (datetime): Cuándo fue revisada
        revisado_por (int): ID del admin que revisó
        usuario (relationship): Usuario que creó la solicitud
        mascota (relationship): Mascota solicitada
        revisor (relationship): Admin que revisó
    """

    __tablename__ = 'solicitudes'

    # Atributos de la tabla
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id'), nullable=False, index=True)
    fecha_solicitud = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    estado = db.Column(db.String(20), nullable=False, default='pendiente', index=True)
    cuestionario_json = db.Column(db.JSON)
    comentarios_admin = db.Column(db.Text)
    fecha_revision = db.Column(db.DateTime)
    revisado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    # Constraint: Un usuario no puede solicitar la misma mascota dos veces
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'mascota_id', name='unique_usuario_mascota'),
    )

    def __init__(self, usuario_id, mascota_id, cuestionario=None):
        """
        Constructor de Solicitud.

        Args:
            usuario_id (int): ID del usuario solicitante
            mascota_id (int): ID de la mascota
            cuestionario (dict): Respuestas del formulario (opcional)
        """
        self.usuario_id = usuario_id
        self.mascota_id = mascota_id
        self.cuestionario_json = cuestionario or {}

    def aprobar(self, admin_id, comentario=None):
        """
        Aprueba la solicitud de adopción.

        Args:
            admin_id (int): ID del administrador que aprueba
            comentario (str): Mensaje para el usuario (opcional)
        """
        self.estado = 'aprobada'
        self.revisado_por = admin_id
        self.fecha_revision = datetime.utcnow()
        self.comentarios_admin = comentario

        # Marcar la mascota como adoptada
        self.mascota.marcar_adoptado()

        db.session.commit()

    def rechazar(self, admin_id, comentario=None):
        """
        Rechaza la solicitud de adopción.

        Args:
            admin_id (int): ID del administrador que rechaza
            comentario (str): Razón del rechazo (opcional)
        """
        self.estado = 'rechazada'
        self.revisado_por = admin_id
        self.fecha_revision = datetime.utcnow()
        self.comentarios_admin = comentario
        db.session.commit()

    def esta_pendiente(self):
        """
        Verifica si la solicitud está pendiente de revisión.

        Returns:
            bool: True si está pendiente
        """
        return self.estado == 'pendiente'

    def __repr__(self):
        """Representación en string del objeto."""
        return f'<Solicitud #{self.id} - Usuario:{self.usuario_id} - Mascota:{self.mascota_id} - {self.estado}>'