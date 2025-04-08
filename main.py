import uvicorn
import os
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения из .env файла
load_dotenv()

# Импортируем адаптер базы данных для инициализации
# Это должно происходить до импорта приложения
import src.db_adapter

if __name__ == "__main__":
    logger.info("Запуск приложения...")
    port = int(os.getenv("PORT", 8080))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Сервер запускается на {host}:{port}")
    uvicorn.run(
        "src.app:app",
        host=host,
        port=port,
        reload=True
    )
    logger.info("Приложение остановлено") 