from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class FormFieldBase(BaseModel):
    """Базовая схема поля формы"""
    field_type: str
    name: str
    label: str
    required: bool = False
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    default_value: Optional[Any] = None
    order: int = 0
    validation: Optional[Dict[str, Any]] = None
    options: Optional[List[Dict[str, Any]]] = None
    conditional_display: Optional[Dict[str, Any]] = None
    
class FormConfigBase(BaseModel):
    """Базовая схема конфигурации формы"""
    business_type: str
    form_type: str
    name: str
    description: Optional[str] = None
    config: Dict[str, Any]
    is_active: bool = True
    version: int = 1

class FormConfigCreate(FormConfigBase):
    """Схема для создания конфигурации формы"""
    pass

class FormConfigUpdate(BaseModel):
    """Схема для обновления конфигурации формы"""
    business_type: Optional[str] = None
    form_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    version: Optional[int] = None
    
class FormConfigInDB(FormConfigBase):
    """Схема конфигурации формы из БД"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        
class FormConfigResponse(FormConfigInDB):
    """Схема ответа с данными конфигурации формы"""
    pass

# Пример конфигурации формы для регистрации компании
EXAMPLE_COMPANY_REGISTRATION_CONFIG = {
    "title": "Регистрация компании",
    "description": "Заполните информацию о вашей компании",
    "submit_label": "Зарегистрировать",
    "fields": [
        {
            "field_type": "text",
            "name": "company_name",
            "label": "Название компании",
            "required": True,
            "placeholder": "Введите название компании",
            "validation": {
                "min_length": 3,
                "max_length": 255
            },
            "order": 1
        },
        {
            "field_type": "select",
            "name": "business_type",
            "label": "Тип бизнеса",
            "required": True,
            "options": [
                {"value": "restaurant", "label": "Ресторан/Кафе"},
                {"value": "beauty", "label": "Салон красоты"},
                {"value": "clinic", "label": "Медицинская клиника"},
                {"value": "service", "label": "Сервисный центр"},
                {"value": "other", "label": "Другое"}
            ],
            "order": 2
        },
        {
            "field_type": "textarea",
            "name": "description",
            "label": "Описание",
            "required": False,
            "placeholder": "Расскажите о вашей компании",
            "order": 3
        },
        {
            "field_type": "text",
            "name": "contact_phone",
            "label": "Контактный телефон",
            "required": True,
            "placeholder": "+7 (XXX) XXX-XX-XX",
            "validation": {
                "pattern": "\\+7 \\(\\d{3}\\) \\d{3}-\\d{2}-\\d{2}"
            },
            "order": 4
        },
        {
            "field_type": "email",
            "name": "contact_email",
            "label": "Электронная почта",
            "required": True,
            "placeholder": "example@domain.com",
            "order": 5
        },
        {
            "field_type": "text",
            "name": "website",
            "label": "Веб-сайт",
            "required": False,
            "placeholder": "https://example.com",
            "order": 6
        },
        {
            "field_type": "file",
            "name": "logo",
            "label": "Логотип",
            "required": False,
            "help_text": "Рекомендуемый размер: 200x200 пикселей",
            "validation": {
                "accepted_types": ["image/jpeg", "image/png"],
                "max_size": 2097152  # 2MB
            },
            "order": 7
        }
    ]
} 