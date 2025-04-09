from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_image(filename, size, text, bg_color=(200, 200, 200), text_color=(100, 100, 100)):
    # Создаем изображение
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Добавляем текст
    text_bbox = draw.textbbox((0, 0), text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    draw.text((x, y), text, fill=text_color)
    
    # Сохраняем изображение
    img.save(filename)

def main():
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    
    # Создаем тестовые изображения
    create_placeholder_image(
        os.path.join(os.path.dirname(__file__), 'placeholder-logo.png'),
        (200, 200),
        'LOGO'
    )
    
    create_placeholder_image(
        os.path.join(os.path.dirname(__file__), 'placeholder-food.png'),
        (300, 200),
        'FOOD'
    )
    
    create_placeholder_image(
        os.path.join(os.path.dirname(__file__), 'placeholder-gallery.png'),
        (400, 300),
        'GALLERY'
    )

if __name__ == '__main__':
    main() 