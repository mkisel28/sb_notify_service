"""Модели для приложения уведомлений."""

import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    """Пользователь, использующий сервис уведомлений."""

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        """Возвращает имя пользователя."""
        return self.username


class Bot(models.Model):
    """Telegram-бот, используемый для отправки уведомлений."""

    name = models.CharField("Название", max_length=255, unique=True)
    token = models.CharField("Токен", max_length=255, unique=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bots",
        verbose_name="Владелец",
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    api_keys: models.Manager["APIKey"]

    class Meta:
        verbose_name = "Бот"
        verbose_name_plural = "Боты"

    def __str__(self) -> str:
        return self.name

    def generate_api_key(self):
        """Создает новый API-ключ для бота (без перезаписи существующих)."""
        return self.api_keys.create(key=APIKey.generate_new_key())

    def get_api_keys(self):
        """Возвращает список всех API-ключей для бота."""
        return self.api_keys.all()


class APIKey(models.Model):
    """API-ключи для аутентификации и привязки к конкретному боту."""

    key = models.CharField("API-key", max_length=255, unique=True)
    bot = models.ForeignKey(
        Bot,
        on_delete=models.CASCADE,
        related_name="api_keys",
        verbose_name="Бот",
    )
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        verbose_name = "API-ключ"
        verbose_name_plural = "API-ключи"

    def __str__(self) -> str:
        return f"{self.bot.name} - {self.key[:10]}..."

    @staticmethod
    def generate_new_key() -> str:
        """Генерирует новый API-ключ."""
        return secrets.token_urlsafe(32)

    def regenerate_key(self):
        """Перегенерирует API-ключ, если он активен."""
        if self.is_active:
            self.key = self.generate_new_key()
            self.updated_at = now()
            self.save()

    def revoke(self):
        """Отзывает API-ключ (деактивирует без удаления)."""
        self.is_active = False
        self.save()

    def activate(self):
        """Активирует API-ключ (если был отозван)."""
        self.is_active = True
        self.save()
