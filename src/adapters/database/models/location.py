# Этот файл теперь переэкспортирует модели из src/models для обратной совместимости
# В новом коде рекомендуется импортировать напрямую из src/models/

from src.models.location import Location

# Класс Location теперь импортируется напрямую из src/models/location.py
# и переэкспортируется здесь для обратной совместимости

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from src.db_adapter import Base


class Location(Base):
    """Модель локации/адреса"""
    __tablename__ = "locations"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    region = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    country = Column(String, nullable=False, default="Россия")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    additional_info = Column(Text, nullable=True)
    
    # Отношения
    company = relationship("Company", back_populates="locations")
    
    def __repr__(self):
        return f"<Location {self.address}, {self.city}>"
    
    def to_dict(self):
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "address": self.address,
            "city": self.city,
            "region": self.region,
            "postal_code": self.postal_code,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "additional_info": self.additional_info,
        } 