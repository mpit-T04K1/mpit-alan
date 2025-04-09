from typing import Any, Dict, Optional, List, Union

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """
    Исключение для случаев, когда объект не найден
    """
    def __init__(
        self, 
        detail: str = "Объект не найден", 
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers)


class UnauthorizedError(HTTPException):
    """
    Исключение для случаев, когда пользователь не авторизован
    """
    def __init__(
        self, 
        detail: str = "Необходима авторизация", 
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers)


class ForbiddenError(HTTPException):
    """
    Исключение для случаев, когда доступ запрещен
    """
    def __init__(
        self, 
        detail: str = "Доступ запрещен", 
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers)


class BadRequestError(HTTPException):
    """
    Исключение для случаев, когда запрос содержит некорректные данные
    """
    def __init__(
        self, 
        detail: Union[str, List[Dict[str, Any]]] = "Некорректный запрос", 
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers)


class ConflictError(HTTPException):
    """
    Исключение для случаев, когда возникает конфликт (например, уникальное поле уже существует)
    """
    def __init__(
        self, 
        detail: str = "Возник конфликт данных", 
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers)


class ValidationError(HTTPException):
    """
    Исключение для случаев, когда данные не проходят валидацию
    """
    def __init__(
        self, 
        detail: Union[str, List[Dict[str, Any]]] = "Ошибка валидации данных", 
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail, headers=headers)


class InternalServerError(HTTPException):
    """
    Исключение для внутренних ошибок сервера
    """
    def __init__(
        self, 
        detail: str = "Внутренняя ошибка сервера", 
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail, headers=headers)


class TelegramError(Exception):
    """
    Исключение для ошибок при работе с Telegram API
    """
    def __init__(self, message: str = "Ошибка при работе с Telegram API"):
        self.message = message
        super().__init__(self.message)


# Обработчики ошибок для API
def not_found_exception_handler(request, exc):
    """
    Обработчик для ошибок 404 Not Found
    """
    return {
        "error": {
            "code": status.HTTP_404_NOT_FOUND,
            "message": str(exc.detail)
        }
    }


def unauthorized_exception_handler(request, exc):
    """
    Обработчик для ошибок 401 Unauthorized
    """
    return {
        "error": {
            "code": status.HTTP_401_UNAUTHORIZED,
            "message": str(exc.detail)
        }
    }


def forbidden_exception_handler(request, exc):
    """
    Обработчик для ошибок 403 Forbidden
    """
    return {
        "error": {
            "code": status.HTTP_403_FORBIDDEN,
            "message": str(exc.detail)
        }
    }


def bad_request_exception_handler(request, exc):
    """
    Обработчик для ошибок 400 Bad Request
    """
    return {
        "error": {
            "code": status.HTTP_400_BAD_REQUEST,
            "message": str(exc.detail) if isinstance(exc.detail, str) else "Некорректный запрос",
            "details": exc.detail if not isinstance(exc.detail, str) else None
        }
    }


def validation_exception_handler(request, exc):
    """
    Обработчик для ошибок 422 Unprocessable Entity
    """
    return {
        "error": {
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Ошибка валидации данных",
            "details": exc.detail if isinstance(exc.detail, list) else None
        }
    } 