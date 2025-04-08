#!/usr/bin/env python3
# template_paths.py - Скрипт для переопределения путей к шаблонам
# Для замены src/templates.py в контейнере

from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

# Настраиваем правильный путь к шаблонам
TEMPLATES_DIR = Path("/app/src/templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Позаботимся о том, чтобы шаблоны были доступны
print(f"Инициализированы шаблоны из директории: {TEMPLATES_DIR}")
print(f"Шаблоны существуют: {TEMPLATES_DIR.exists()}")
if TEMPLATES_DIR.exists():
    print(f"Доступные шаблоны: {list(TEMPLATES_DIR.glob('*.html'))}") 