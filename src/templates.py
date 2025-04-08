from typing import Any

from fastapi import Request
from fastapi.templating import Jinja2Templates
from src.settings import settings


# Создаем экземпляр Jinja2Templates для использования в приложении
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

def https_url_for(request: Request, name: str, **path_params: Any) -> str:
    url = settings.MAIN_PATH + name
    if path_params:
        params = [f"{name}={value}" for name, value in path_params.items()]
        url += "?" + "&".join(params)
    return url

templates.env.globals["https_url_for"] = https_url_for