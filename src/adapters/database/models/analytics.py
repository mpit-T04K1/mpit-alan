from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from src.db_adapter import Base
from src.models.analytics import Analytics

# Класс Analytics теперь импортируется напрямую из src/models/analytics.py
# и переэкспортируется здесь для обратной совместимости