import boto3
from botocore.client import Config

from src.settings import settings


def s3_session_factory():
    """Фабрика сессий для S3"""
    # Если не заданы настройки S3, возвращаем None
    if not all([settings.S3_ENDPOINT, settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY]):
        return None
    
    # Создаем клиент S3
    s3_client = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY.get_secret_value() if settings.S3_SECRET_KEY else None,
        region_name=settings.S3_REGION,
        config=Config(signature_version="s3v4")
    )
    
    return s3_client 