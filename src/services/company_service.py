from sqlalchemy.ext.asyncio import AsyncSession


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db
