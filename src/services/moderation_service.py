from sqlalchemy.ext.asyncio import AsyncSession


class ModerationService:
    def __init__(self, db: AsyncSession):
        self.db = db
