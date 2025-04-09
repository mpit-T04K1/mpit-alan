from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import os
import logging
import json
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# Импортируем маршруты
try:
    from app.routes import situation_center
    from app.routes import business_registration
except ImportError:
    # Если не удается импортировать из пакета app, попробуем относительные импорты
    logging.warning("Не удалось импортировать маршруты из пакета app, попытка альтернативного импорта")
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from routes import situation_center
        from routes import business_registration
    except ImportError:
        logging.error("Не удалось импортировать маршруты")

# Определяем модели из panel_config.py напрямую
class MenuItem(BaseModel):
    """Модель для позиции меню"""
    id: str
    name: str
    price: float
    description: Optional[str] = None
    image: Optional[str] = None

class MenuCategory(BaseModel):
    """Модель для категории меню"""
    id: str
    name: str
    items: List[MenuItem] = Field(default_factory=list)

class MenuConfig(BaseModel):
    """Модель конфигурации меню"""
    categories: List[MenuCategory] = Field(default_factory=list)

class PanelConfig(BaseModel):
    """Модель конфигурации панелей интерфейса"""
    business_id: str
    panels: Dict[str, bool]  # ID панели -> активна/неактивна
    order: Optional[Dict[str, int]] = None  # ID панели -> порядок отображения
    menu: Optional[MenuConfig] = None  # Конфигурация меню

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из .env файла
load_dotenv()

# Создание экземпляра FastAPI
app = FastAPI(
    title="Qwerty.town - Модульный интерфейс",
    description="Демонстрация модульного интерфейса",
    version="0.1.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Настройка шаблонов
templates = Jinja2Templates(directory="app/templates")

# Подключаем роутеры
app.include_router(situation_center.router)
app.include_router(business_registration.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Главная страница с модульным интерфейсом
    """
    return templates.TemplateResponse(
        "cafe_example.html", 
        {
            "request": request,
            "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
        }
    )

@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    """
    Тестовая страница с данными последнего зарегистрированного бизнеса из JSON
    """
    logger.debug("Обработка запроса к маршруту /test")
    try:
        # Загружаем данные о бизнесах из JSON файла
        from pathlib import Path
        
        # Путь к файлу с данными
        json_path = Path("app/data/businesses.json")
        
        # Проверяем существование файла
        if json_path.exists():
            # Загружаем данные
            with open(json_path, "r", encoding="utf-8") as f:
                businesses_data = json.load(f)
                
            if businesses_data:
                # Получаем последний добавленный бизнес (последний ключ в словаре)
                last_business_id = list(businesses_data.keys())[-1]
                business = businesses_data[last_business_id]
                logger.info(f"Загружены данные последнего бизнеса: {business['name']}")
                
                # Проверяем наличие конфигурации
                config_path = Path(f"app/data/configs/{business['id']}.json")
                config = None
                
                if config_path.exists():
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            config = json.load(f)
                        logger.info(f"Загружена конфигурация для бизнеса: {business['name']}")
                    except Exception as e:
                        logger.error(f"Ошибка при загрузке конфигурации: {e}")
                
                return templates.TemplateResponse(
                    "business.html",
                    {
                        "request": request, 
                        "business": business,
                        "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", ""),
                        "config": config
                    }
                )
            else:
                logger.warning("Файл businesses.json пуст")
                return templates.TemplateResponse(
                    "business.html",
                    {
                        "request": request,
                        "error": "Нет зарегистрированных бизнесов",
                        "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
                    }
                )
        else:
            logger.error(f"Файл с данными не найден: {json_path}")
            return templates.TemplateResponse(
                "business.html",
                {
                    "request": request,
                    "error": "Файл данных не найден",
                    "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
                }
            )
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        return templates.TemplateResponse(
            "business.html",
            {
                "request": request,
                "error": str(e),
                "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
            }
        )

@app.get("/test/constructor", response_class=HTMLResponse)
async def test_constructor_page(request: Request):
    """
    Конструктор для тестовой страницы бизнеса
    """
    logger.debug("Обработка запроса к маршруту /test/constructor")
    try:
        # Загружаем данные о бизнесах из JSON файла
        from pathlib import Path
        
        # Путь к файлу с данными
        json_path = Path("app/data/businesses.json")
        
        # Проверяем существование файла
        if json_path.exists():
            # Загружаем данные
            with open(json_path, "r", encoding="utf-8") as f:
                businesses_data = json.load(f)
                
            if businesses_data:
                # Получаем последний добавленный бизнес (последний ключ в словаре)
                last_business_id = list(businesses_data.keys())[-1]
                business = businesses_data[last_business_id]
                logger.info(f"Загружены данные последнего бизнеса: {business['name']}")
                
                # Проверяем наличие конфигурации
                config_path = Path(f"app/data/configs/{business['id']}.json")
                config = None
                
                if config_path.exists():
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            config = json.load(f)
                        logger.info(f"Загружена конфигурация для бизнеса: {business['name']}")
                    except Exception as e:
                        logger.error(f"Ошибка при загрузке конфигурации: {e}")
                
                return templates.TemplateResponse(
                    "constructor.html",
                    {
                        "request": request, 
                        "business": business,
                        "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", ""),
                        "config": config
                    }
                )
            else:
                logger.warning("Файл businesses.json пуст")
                return templates.TemplateResponse(
                    "constructor.html",
                    {
                        "request": request,
                        "error": "Нет зарегистрированных бизнесов",
                        "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
                    }
                )
        else:
            logger.error(f"Файл с данными не найден: {json_path}")
            return templates.TemplateResponse(
                "constructor.html",
                {
                    "request": request,
                    "error": "Файл данных не найден",
                    "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
                }
            )
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        return templates.TemplateResponse(
            "constructor.html",
            {
                "request": request,
                "error": str(e),
                "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
            }
        )

@app.get("/constructor", response_class=HTMLResponse)
async def constructor_page(request: Request):
    """
    Страница конструктора меню с данными последнего зарегистрированного бизнеса из JSON
    """
    logger.debug("Обработка запроса к маршруту /constructor")
    try:
        # Загружаем данные о бизнесах из JSON файла
        from pathlib import Path
        
        # Путь к файлу с данными
        json_path = Path("app/data/businesses.json")
        
        # Проверяем существование файла
        if json_path.exists():
            # Загружаем данные
            with open(json_path, "r", encoding="utf-8") as f:
                businesses_data = json.load(f)
                
            if businesses_data:
                # Получаем последний добавленный бизнес (последний ключ в словаре)
                last_business_id = list(businesses_data.keys())[-1]
                business = businesses_data[last_business_id]
                logger.info(f"Загружены данные последнего бизнеса: {business['name']}")
                
                # Проверяем наличие конфигурации
                config_path = Path(f"app/data/configs/{business['id']}.json")
                config = None
                
                if config_path.exists():
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            config = json.load(f)
                        logger.info(f"Загружена конфигурация для бизнеса: {business['name']}")
                    except Exception as e:
                        logger.error(f"Ошибка при загрузке конфигурации: {e}")
                
                return templates.TemplateResponse(
                    "constructor.html",
                    {
                        "request": request, 
                        "business": business,
                        "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", ""),
                        "config": config
                    }
                )
            else:
                logger.warning("Файл businesses.json пуст")
                return templates.TemplateResponse(
                    "constructor.html",
                    {
                        "request": request,
                        "error": "Нет зарегистрированных бизнесов",
                        "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
                    }
                )
        else:
            logger.error(f"Файл с данными не найден: {json_path}")
            return templates.TemplateResponse(
                "constructor.html",
                {
                    "request": request,
                    "error": "Файл данных не найден",
                    "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
                }
            )
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        return templates.TemplateResponse(
            "constructor.html",
            {
                "request": request,
                "error": str(e),
                "yandex_maps_api_key": os.getenv("YANDEX_MAPS_API_KEY", "")
            }
        )

@app.post("/api/save-config")
async def save_config(config: PanelConfig):
    """
    Сохраняет конфигурацию для бизнеса
    """
    logger.info(f"Сохранение конфигурации для бизнеса: {config.business_id}")
    
    try:
        # Путь к файлу конфигурации
        config_dir = Path("app/data/configs")
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / f"{config.business_id}.json"
        
        # Сохраняем конфигурацию
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config.dict(), f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "message": "Конфигурация успешно сохранена"}
    except Exception as e:
        logger.error(f"Ошибка при сохранении конфигурации: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )

if __name__ == "__main__":
    # Запуск сервера
    import sys
    # Определяем, запущен ли скрипт как модуль или напрямую
    module_name = "main:app"
    if __package__ is not None:
        # Если скрипт запущен как модуль, используем правильное имя модуля
        module_name = f"{__name__.split('.')[0]}.main:app"
    
    # Настройка порта
    port = int(os.getenv("PORT", 9090))
    
    logger.info(f"Запуск сервера на порту {port}, модуль: {module_name}")
    
    uvicorn.run(
        module_name,
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    ) 