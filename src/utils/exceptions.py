class BaseAppException(Exception):
    """Базовое исключение приложения"""
    pass


class ResultNotFound(BaseAppException):
    """Результат не найден в базе данных"""
    pass


class AuthenticationError(BaseAppException):
    """Ошибка аутентификации"""
    pass


class AuthorizationError(BaseAppException):
    """Ошибка авторизации"""
    pass


class ValidationError(BaseAppException):
    """Ошибка валидации данных"""
    pass


class UserAlreadyExists(BaseAppException):
    """Пользователь уже существует"""
    pass


class InvalidCredentials(BaseAppException):
    """Неверные учетные данные"""
    pass


class TokenError(BaseAppException):
    """Ошибка с токеном"""
    pass


class PermissionDenied(BaseAppException):
    """Доступ запрещен"""
    pass


class FileStorageError(BaseAppException):
    """Ошибка при работе с файловым хранилищем"""
    pass


class TelegramError(BaseAppException):
    """Ошибка при работе с Telegram API"""
    pass 