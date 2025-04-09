from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import os
from pathlib import Path
import logging

# Пытаемся импортировать модель PanelConfig
try:
    from app.models.panel_config import PanelConfig
except ImportError:
    logging.warning("Не удалось импортировать PanelConfig из app.models, использую локальное определение")
    from pydantic import BaseModel, Field
    from typing import Dict, List, Optional
    
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

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/business/{business_id}", response_class=HTMLResponse)
async def get_business_page(request: Request, business_id: str):
    try:
        # Загружаем данные о бизнесах из JSON файла
        with open("app/data/businesses.json", "r", encoding="utf-8") as f:
            businesses = json.load(f)
        
        # Ищем бизнес по ID
        business = businesses.get(business_id)
        
        if not business:
            raise HTTPException(status_code=404, detail="Бизнес не найден")
        
        # Загружаем конфигурацию панелей, если она существует
        config = None
        config_path = Path(f"app/data/configs/{business_id}.json")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        
        # Возвращаем шаблон с данными о бизнесе и конфигурацией
        return templates.TemplateResponse(
            "business.html",
            {
                "request": request, 
                "business": business,
                "config": config
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Файл с данными не найден")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Ошибка при чтении данных")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/business/save-config")
async def save_config(config: PanelConfig):
    """
    Сохраняет конфигурацию панелей для бизнеса (альтернативный путь)
    """
    try:
        print(f"Обработка запроса на сохранение конфигурации в business.py для бизнеса {config.business_id}")
        print(f"Данные конфигурации: {config.dict()}")
        
        # Создаем директорию для конфигураций, если её нет
        config_dir = Path("app/data/configs")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Путь к файлу конфигурации
        config_path = config_dir / f"{config.business_id}.json"
        
        # Сохраняем конфигурацию
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config.dict(), f, ensure_ascii=False, indent=2)
        
        print(f"Конфигурация сохранена в business.py для {config.business_id}")
        
        # Если в конфигурации есть меню, обновляем также и бизнес
        if config.menu and hasattr(config.menu, 'categories'):
            try:
                # Загружаем данные о бизнесах
                with open("app/data/businesses.json", "r", encoding="utf-8") as f:
                    businesses = json.load(f)
                
                # Обновляем меню бизнеса
                if config.business_id in businesses:
                    # Преобразуем категории меню в формат для JSON
                    categories_dict = []
                    for category in config.menu.categories:
                        category_dict = category.dict()
                        categories_dict.append(category_dict)
                    
                    # Обновляем меню
                    businesses[config.business_id]["menu"] = {"categories": categories_dict}
                    
                    # Сохраняем обновленные данные
                    with open("app/data/businesses.json", "w", encoding="utf-8") as f:
                        json.dump(businesses, f, ensure_ascii=False, indent=2)
                    
                    print(f"Меню бизнеса обновлено в business.py для {config.business_id}")
            except Exception as e:
                # Логируем ошибку, но не прерываем выполнение
                print(f"Ошибка при обновлении меню бизнеса в business.py: {str(e)}")
        
        return {"status": "success", "message": "Конфигурация успешно сохранена"}
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации в business.py: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/business/{business_id}/constructor", response_class=HTMLResponse)
async def constructor_page(request: Request, business_id: str):
    """
    Страница конструктора интерфейса для бизнеса
    """
    try:
        # Загружаем данные о бизнесе
        with open("app/data/businesses.json", "r", encoding="utf-8") as f:
            businesses = json.load(f)
        
        business = businesses.get(business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Бизнес не найден")
        
        # Загружаем текущую конфигурацию, если она существует
        config = None
        config_path = Path(f"app/data/configs/{business_id}.json")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        
        return templates.TemplateResponse(
            "constructor.html",
            {
                "request": request,
                "business": business,
                "config": config
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 