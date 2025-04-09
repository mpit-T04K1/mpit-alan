from typing import Any
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import time
import random
from pathlib import Path as PathLib

# Настройка шаблонов
templates_dir = PathLib(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))
def https_url_for(name: str, **path_params: Any) -> str:
    url = os.getenv("MAIN_PATH") + name
    if path_params:
        params = [f"{name}={value}" for name, value in path_params.items()]
        url += "?" + "&".join(params)
    return url

templates.env.globals["https_url_for"] = https_url_for

# Создаем роутер для ситуационного центра
router = APIRouter(
    prefix="/situation-center",
    tags=["situation_center"],
    responses={404: {"description": "Not found"}},
)

@router.get("/modular-demo", response_class=HTMLResponse)
async def modular_interface_demo(request: Request):
    """
    Демонстрация модульного интерфейса с тремя панелями.
    """
    return templates.TemplateResponse(
        "cafe_example.html", 
        {
            "request": request,
            "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
        }
    )

@router.get("/api/items", response_class=JSONResponse)
async def get_items():
    """
    API для получения списка элементов для левой панели.
    """
    # Симуляция задержки
    time.sleep(0.5)
    
    # Генерируем тестовые данные
    items = []
    
    # Создаем разные типы элементов
    statuses = ["success", "warning", "danger", "info", ""]
    
    # Создаем тестовые элементы
    for i in range(1, 21):
        status = random.choice(statuses)
        item = {
            "id": f"item-{i}",
            "title": f"Элемент {i}",
            "subtitle": f"Описание элемента {i}",
            "status": status,
            "badge": random.randint(0, 5) if random.random() > 0.7 else None
        }
        items.append(item)
    
    return {"items": items}

@router.get("/api/items/{item_id}", response_class=JSONResponse)
async def get_item_details(item_id: str):
    """
    API для получения детальной информации об элементе.
    """
    # Симуляция задержки
    time.sleep(0.5)
    
    # Проверяем существование элемента
    if not item_id.startswith("item-"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Элемент не найден"}
        )
    
    # Создаем тестовые данные для элемента
    item_number = item_id.split("-")[1]
    
    item_details = {
        "id": item_id,
        "title": f"Элемент {item_number}",
        "description": f"Подробное описание элемента {item_number}",
        "status": random.choice(["success", "warning", "danger", "info", ""]),
        "created_at": "2023-01-01T12:00:00Z",
        "updated_at": "2023-01-02T15:30:00Z",
        "metadata": {
            "author": "Система",
            "category": "Тестовая категория",
            "priority": random.randint(1, 5),
            "tags": ["тест", "демо", "пример"]
        }
    }
    
    return item_details 