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