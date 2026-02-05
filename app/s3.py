import boto3
import uuid
from flask import current_app

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida."""
    return "." in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def upload_to_s3(file):
    """Sube un archivo a S3 y retorna la URL pública."""
    if not allowed_file(file.filename):
        return None

    # Nombre único para evitar colisiones
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"mascotas/{uuid.uuid4().hex}.{ext}"

    s3 = boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_S3_REGION']
    )

    s3.upload_fileobj(
        file,
        current_app.config['AWS_S3_BUCKET'],
        filename,
        ExtraArgs={'ContentType': file.content_type}
    )

    bucket = current_app.config['AWS_S3_BUCKET']
    region = current_app.config['AWS_S3_REGION']
    return f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"

def delete_from_s3(url):
    """Elimina un archivo de S3 por su URL."""
    if not url or 'amazonaws.com' not in url:
        return

    key = url.split('.amazonaws.com/')[1]

    s3 = boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_S3_REGION']
    )

    s3.delete_object(
        Bucket=current_app.config['AWS_S3_BUCKET'],
        Key=key
    )