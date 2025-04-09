"""
Модуль для проверки прав доступа пользователей в приложении
"""

from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db_adapter import get_db
from src.services.auth_service import get_current_user
from src.models.user import UserRole
from src.schemas.user import UserResponse


# Функции для проверки прав доступа

async def is_authenticated(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Проверяет, что пользователь аутентифицирован"""
    return current_user


async def is_active(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Проверяет, что пользователь активен"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт неактивен"
        )
    return current_user


async def is_admin(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Проверяет, что пользователь имеет права администратора"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return current_user


async def is_business(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Проверяет, что пользователь имеет права бизнес-аккаунта"""
    if current_user.role not in [UserRole.ADMIN, UserRole.COMPANY_OWNER, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется бизнес-аккаунт"
        )
    return current_user


async def is_company_owner(
    company_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Проверяет, что пользователь является владельцем компании
    
    Args:
        company_id: ID компании
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        Объект пользователя, если проверка пройдена
        
    Raises:
        HTTPException: Если пользователь не является владельцем компании
    """
    # Для администратора разрешаем доступ к любой компании
    if current_user.role == UserRole.ADMIN:
        return current_user
    
    # Проверяем, является ли пользователь владельцем
    from src.repositories.company import CompanyRepository
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Компания не найдена"
        )
    
    if company.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен: вы не являетесь владельцем этой компании"
        )
    
    return current_user


async def can_manage_company(
    company_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Проверяет, что пользователь может управлять компанией
    (владелец, менеджер или администратор)
    
    Args:
        company_id: ID компании
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        Объект пользователя, если проверка пройдена
        
    Raises:
        HTTPException: Если пользователь не может управлять компанией
    """
    # Для администратора разрешаем доступ к любой компании
    if current_user.role == UserRole.ADMIN:
        return current_user
    
    # Проверяем, является ли пользователь владельцем или менеджером
    from src.repositories.company import CompanyRepository
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Компания не найдена"
        )
    
    if company.owner_id == current_user.id:
        return current_user
    
    # TODO: Добавить проверку на менеджера компании, когда будет реализована такая функциональность
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Доступ запрещен: у вас нет прав на управление этой компанией"
    )


async def check_company_permission(db: AsyncSession, current_user: UserResponse, company_id: int) -> bool:
    """
    Проверяет права доступа пользователя к компании
    
    Args:
        db: Сессия базы данных
        current_user: Текущий пользователь
        company_id: ID компании
        
    Returns:
        True, если пользователь имеет доступ к компании
        
    Raises:
        HTTPException: Если пользователь не имеет доступа к компании
    """
    # Для администратора разрешаем доступ к любой компании
    if current_user.role == UserRole.ADMIN:
        return True
    
    # Проверяем, является ли пользователь владельцем или менеджером
    from src.repositories.company import CompanyRepository
    company_repo = CompanyRepository(db)
    company = await company_repo.get_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Компания не найдена"
        )
    
    if company.owner_id == current_user.id:
        return True
    
    # TODO: Добавить проверку на менеджера компании, когда будет реализована такая функциональность
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Доступ запрещен: у вас нет прав на доступ к этой компании"
    ) 