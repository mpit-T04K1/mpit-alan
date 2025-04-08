from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from src.settings import settings


# Создаем экземпляр Jinja2Templates для использования в приложении
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

def https_url_for(request: Request, name: str, **path_params: Any) -> str:

    http_url = request.url_for(name, **path_params)

    # Replace 'http' with 'https'
    return http_url.replace("http", "https", 1)

templates.env.globals["https_url_for"] = https_url_for