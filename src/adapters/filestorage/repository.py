import os
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from typing import BinaryIO, Optional, Protocol

from botocore.exceptions import ClientError

from src.settings import settings
from src.utils.exceptions import FileStorageError


class FileStorageProtocol(Protocol):
    """Протокол для работы с файловым хранилищем"""
    
    async def upload_file(self, file: BinaryIO, folder: str, filename: Optional[str] = None) -> str:
        """Загрузить файл в хранилище"""
        ...
    
    async def delete_file(self, file_path: str) -> bool:
        """Удалить файл из хранилища"""
        ...
    
    async def get_file_url(self, file_path: str, expires: Optional[int] = None) -> str:
        """Получить URL файла"""
        ...


class FileStorageRepository:
    """Репозиторий для работы с файловым хранилищем (S3)"""
    
    def __init__(self, s3_client):
        self.s3_client = s3_client
        self.bucket = settings.S3_BUCKET
    
    async def upload_file(self, file: BinaryIO, folder: str, filename: Optional[str] = None) -> str:
        """Загрузить файл в хранилище"""
        if self.s3_client is None:
            raise FileStorageError("S3 client is not configured")
        
        # Генерируем имя файла, если не указано
        if not filename:
            ext = os.path.splitext(getattr(file, "filename", ""))[1] or ""
            filename = f"{uuid.uuid4()}{ext}"
        
        # Формируем путь к файлу
        file_path = f"{folder}/{filename}"
        
        try:
            # Загружаем файл в S3
            self.s3_client.upload_fileobj(file, self.bucket, file_path)
            return file_path
        except ClientError as e:
            raise FileStorageError(f"Failed to upload file: {e}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Удалить файл из хранилища"""
        if self.s3_client is None:
            raise FileStorageError("S3 client is not configured")
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=file_path)
            return True
        except ClientError as e:
            raise FileStorageError(f"Failed to delete file: {e}")
    
    async def get_file_url(self, file_path: str, expires: Optional[int] = None) -> str:
        """Получить URL файла"""
        if self.s3_client is None:
            raise FileStorageError("S3 client is not configured")
        
        # Если файл не существует, возвращаем None
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=file_path)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise FileStorageError(f"File not found: {file_path}")
            else:
                raise FileStorageError(f"Failed to check file existence: {e}")
        
        # Если файл существует, генерируем URL
        try:
            expiration = expires or 3600  # По умолчанию 1 час
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": file_path},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise FileStorageError(f"Failed to generate file URL: {e}") 