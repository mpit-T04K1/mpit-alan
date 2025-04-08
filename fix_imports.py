#!/usr/bin/env python
"""
Скрипт для исправления импортов в файлах проекта.
"""
import os
import re
import glob
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Корневая директория проекта
PROJECT_ROOT = Path(__file__).parent

# Шаблоны замены
REPLACEMENTS = [
    (r'from src\.db\.database import Base', 'from src.db_adapter import Base'),
    (r'from src\.database import Base', 'from src.db_adapter import Base'),
    (r'from src\.adapters\.database\.session import Base', 'from src.db_adapter import Base'),
    
    # Замены для других функций
    (r'from src\.db\.database import (get_db|check_db_connection|engine|async_session_factory)', 
     r'from src.db_adapter import \1'),
    (r'from src\.database import (get_db|check_db_connection|engine|async_session_factory)', 
     r'from src.db_adapter import \1'),
    (r'from src\.adapters\.database\.session import (get_db|check_db_connection|engine|async_session_maker)', 
     r'from src.db_adapter import \1'),
]

def fix_imports_in_file(file_path):
    """Исправляет импорты в указанном файле"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, нужно ли обрабатывать этот файл
    if 'Base' not in content and 'get_db' not in content and 'check_db_connection' not in content:
        return False
    
    original_content = content
    # Применяем каждую замену
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)
    
    # Если файл изменился, записываем изменения
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f'Исправлен файл: {file_path}')
        return True
    
    return False

def main():
    """Основная функция скрипта"""
    logger.info('Начало исправления импортов...')
    
    # Получаем все Python-файлы в проекте
    python_files = glob.glob(str(PROJECT_ROOT / 'src/**/*.py'), recursive=True)
    
    total_files = len(python_files)
    fixed_files = 0
    
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_files += 1
    
    logger.info(f'Обработка завершена. Исправлено файлов: {fixed_files}/{total_files}')

if __name__ == '__main__':
    main() 