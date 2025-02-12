import uuid
from pathlib import Path


def generate_unique_filename(instance, filename) -> Path:
    """Генерирует уникальное имя для изображения c UUID."""
    ext = filename.split(".")[-1]
    new_filename = f"{uuid.uuid4()}.{ext}"
    return Path("photos") / new_filename
