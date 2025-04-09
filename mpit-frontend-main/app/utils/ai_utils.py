import json
import time
import requests
import base64
from pathlib import Path
import os

class FusionBrainAPI:
    def __init__(self, url="https://api-key.fusionbrain.ai/", api_key=None, secret_key=None):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key or os.getenv("FUSION_BRAIN_API_KEY")}',
            'X-Secret': f'Secret {secret_key or os.getenv("FUSION_BRAIN_SECRET_KEY")}',
        }

    def get_pipeline(self):
        """Получение ID пайплайна для генерации изображений"""
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
        """Запуск генерации изображения"""
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt
            }
        }

        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        """Проверка статуса генерации и получение результата"""
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']

            attempts -= 1
            time.sleep(delay)
        return None

    def save_generated_image(self, base64_data, business_id, image_type="logo"):
        """Сохранение сгенерированного изображения"""
        try:
            # Создаем директории для сохранения, если их нет
            upload_dir = Path("app/static/uploads")
            if image_type == "logo":
                save_dir = upload_dir / "logos"
            else:
                save_dir = upload_dir / "gallery"
            
            save_dir.mkdir(parents=True, exist_ok=True)

            # Генерируем имя файла
            filename = f"{business_id}.png"
            file_path = save_dir / filename

            # Декодируем и сохраняем изображение
            image_data = base64.b64decode(base64_data)
            with open(file_path, "wb") as f:
                f.write(image_data)

            # Возвращаем путь к файлу относительно static директории
            return f"/static/uploads/{'logos' if image_type == 'logo' else 'gallery'}/{filename}"
        except Exception as e:
            print(f"Ошибка при сохранении изображения: {e}")
            return None

    def create_logo_prompt(self, business_description, business_type="cafe"):
        """Создание промпта для генерации логотипа"""
        if not business_description or len(business_description) < 10:
            return "Современный минималистичный логотип для бизнеса"

        # Формируем базовый промпт на русском языке
        base_prompt = f"Создай современный профессиональный логотип для {business_type}. "
        base_prompt += f"Учти следующее описание: {business_description}. "
        base_prompt += "Логотип должен быть минималистичным, запоминающимся и подходящим для использования в разных размерах. "
        base_prompt += "Используй современные тенденции дизайна."

        return base_prompt 