async def get_current_user_optional(
    request: Request = None,
    token: Optional[str] = None, 
    db: AsyncSession = Depends(get_db)
) -> Optional[UserResponse]:
    """
    Опциональная проверка пользователя - возвращает реального пользователя по токену
    или тестового пользователя для режима разработки.
    
    Args:
        request: Запрос (опционально)
        token: Токен (опционально)
        db: Сессия базы данных
        
    Returns:
        Пользователь или None
    """
    if request and ('admin' in request.url.path or 'business' in request.url.path):
        # Для админки и бизнес-модуля возвращаем тестового пользователя
        test_user = UserResponse(
            id=9999,
            email="admin@example.com",
            first_name="Test",
            last_name="Admin",
            role="admin",
            is_active=True,
            is_superuser=True,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        logger.info(f"Using test admin user: {test_user.email} with role: {test_user.role}")
        return test_user
    
    # Для всех остальных - пытаемся получить пользователя по токену
    if token:
        try:
            if not token and request:
                token = await get_token_from_request(request)
                
            if token:
                # Декодируем токен
                try:
                    payload = jwt.decode(
                        token,
                        settings.JWT_SECRET_KEY,
                        algorithms=[settings.JWT_ALGORITHM]
                    )
                    subject = payload.get("sub")
                    
                    if subject:
                        # Ищем пользователя
                        user_repo = UserRepository(db)
                        if subject.isdigit():
                            user = await user_repo.get_by_id(int(subject))
                        else:
                            user = await user_repo.get_by_email(subject)
                            
                        if user:
                            return user
                except JWTError:
                    pass
        except Exception as e:
            logger.error(f"Error in get_current_user_optional: {str(e)}")
            
    # Если ничего не сработало, возвращаем None
    return None
