from sqlalchemy.ext.asyncio import AsyncSession

class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db