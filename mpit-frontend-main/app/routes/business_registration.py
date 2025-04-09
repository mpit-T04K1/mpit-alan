from typing import Optional
from fastapi import APIRouter, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uuid
from pathlib import Path
from app.utils.ai_utils import FusionBrainAPI

from sqlalchemy import insert, select

from app.database.session import async_session_maker
from app.database.models import Company, BusinessType


# Настройка шаблонов
templates_dir = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Путь к файлу с данными о бизнесах
businesses_file = Path(__file__).resolve().parent.parent / "data" / "businesses.json"

# Создаем роутер для регистрации бизнеса
router = APIRouter(
    prefix="/business",
    tags=["business_registration"],
    responses={404: {"description": "Not found"}},
)

class LogoGenerationRequest(BaseModel):
    description: str
    business_type: str

@router.get("/register", response_class=HTMLResponse)
async def business_registration_page(request: Request):
    """
    Страница регистрации бизнеса
    """
    return templates.TemplateResponse(
        "business_registration.html", 
        {
            "request": request,
            "title": "Регистрация бизнеса"
        }
    )

@router.post("/register")
async def register_business(
    business_name: str = Form(...),
    business_type: str = Form(...),
    address: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    description: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None)
):  
    print(business_type)
    print(dict(
        name=business_name,
        business_type=BusinessType[business_type],
        address=address,
        phone=phone,
        email=email,
        description=description,
        logo="logo"
    ))
    async with async_session_maker() as session:
        stmt = insert(Company).values(
            name=business_name,
            business_type=BusinessType[business_type],
            address=address,
            phone=phone,
            email=email,
            description=description,
            logo="logo"
        ).returning(Company)
        result = await session.execute(stmt)
        await session.commit()
        result = result.scalar()
    return {"business_id": result.id}



@router.get("/{business_id}")
async def get_business(business_id: int):
    async with async_session_maker() as session:
        stmt = select(Company).where(Company.id == business_id)
        res = await session.execute(stmt)
        res: Company = res.scalar()
        record = {
            "businessName": res.name,
            "businessType": res.business_type,
            "address": res.address,
            "contactPhone": res.phone,
            "email": res.phone,
            "description": res.description,
            "logo": res.logo
        }


@router.post("/generate-logo")
async def generate_logo(request: LogoGenerationRequest):
    """
    Генерация логотипа с помощью Fusion Brain API
    """
    try:
        # Инициализируем API
        api = FusionBrainAPI()
        
        # Получаем ID пайплайна
        pipeline_id = api.get_pipeline()
        
        # Создаем промпт для логотипа
        prompt = api.create_logo_prompt(request.description, request.business_type)
        
        # Генерируем изображение
        uuid_str = api.generate(prompt, pipeline_id)
        
        # Получаем результат
        files = api.check_generation(uuid_str)
        
        if not files:
            raise HTTPException(status_code=500, detail="Не удалось сгенерировать логотип")
        
        # Генерируем временный ID для сохранения
        temp_id = str(uuid.uuid4())
        
        # Сохраняем логотип
        logo_path = api.save_generated_image(files[0], temp_id, "logo")
        
        if not logo_path:
            raise HTTPException(status_code=500, detail="Не удалось сохранить логотип")
        
        return JSONResponse(content={"logo_path": logo_path})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 