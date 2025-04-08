from fastapi.templating import Jinja2Templates
from src.settings import settings

# Создаем экземпляр Jinja2Templates для использования в приложении
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR) 