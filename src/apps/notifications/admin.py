from django.contrib import admin, messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import APIKey, Bot


class APIKeyInline(TabularInline):
    """Отображение API-ключей в карточке бота."""

    model = APIKey
    extra = 0
    readonly_fields = ("key", "created_at", "is_active", "api_key_actions")

    def api_key_actions(self, obj):
        """Добавляет стилизованные кнопки для управления API-ключами с Tailwind."""
        actions = []

        if obj.is_active:
            actions.append(
                f'<a href="/adminpanelsbnotify/notifications/apikey/{obj.id}/regenerate/" '
                'class="px-3 py-1 text-sm font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700 transition">'
                "Перегенерировать</a>",
            )
            actions.append(
                f'<a href="/adminpanelsbnotify/notifications/apikey/{obj.id}/revoke/" '
                'class="px-3 py-1 text-sm font-semibold text-white bg-yellow-500 rounded-md hover:bg-yellow-600 transition">'
                "Отозвать</a>",
            )
        else:
            actions.append(
                f'<a href="/adminpanelsbnotify/notifications/apikey/{obj.id}/activate/" '
                'class="px-3 py-1 text-sm font-semibold text-white bg-green-600 rounded-md hover:bg-green-700 transition">'
                "Активировать</a>",
            )

        actions.append(
            f'<a href="/adminpanelsbnotify/notifications/apikey/{obj.id}/delete/" '
            'class="px-3 py-1 text-sm font-semibold text-white bg-red-600 rounded-md hover:bg-red-700 transition">'
            "Удалить</a>",
        )

        return format_html(" ".join(actions))

    api_key_actions.short_description = "Действия"


@admin.register(APIKey)
class APIKeyAdmin(ModelAdmin):
    list_display = ("bot", "key", "is_active", "created_at")

    def get_urls(self):
        """Добавляет кастомные URL в админку для API-ключей."""
        custom_urls = [
            path("<int:key_id>/regenerate/", self.regenerate_key),
            path("<int:key_id>/revoke/", self.revoke_key),
            path("<int:key_id>/activate/", self.activate_key),
            path("<int:key_id>/delete/", self.delete_key),
        ]
        return custom_urls + super().get_urls()

    def regenerate_key(self, request, key_id):
        """Перегенерация API-ключа."""
        api_key = get_object_or_404(APIKey, id=key_id)
        api_key.regenerate_key()
        messages.success(
            request,
            f"API-ключ успешно перегенерирован: {api_key.key[:10]}...",
        )
        return redirect(
            request.META.get("HTTP_REFERER", "/admin/notifications/apikey/"),
        )

    def revoke_key(self, request, key_id):
        """Отзыв API-ключа (деактивация)."""
        api_key = get_object_or_404(APIKey, id=key_id)
        api_key.revoke()
        messages.success(request, f"API-ключ для {api_key.bot.name} отозван.")
        return redirect(
            request.META.get("HTTP_REFERER", "/admin/notifications/apikey/"),
        )

    def activate_key(self, request, key_id):
        """Активация API-ключа."""
        api_key = get_object_or_404(APIKey, id=key_id)
        api_key.activate()
        messages.success(
            request,
            f"API-ключ для {api_key.bot.name} активирован.",
        )
        return redirect(
            request.META.get("HTTP_REFERER", "/admin/notifications/apikey/"),
        )

    def delete_key(self, request, key_id):
        """Полное удаление API-ключа."""
        api_key = get_object_or_404(APIKey, id=key_id)
        bot_name = api_key.bot.name
        api_key.delete()
        messages.success(request, f"API-ключ для {bot_name} удален.")
        return redirect(
            request.META.get("HTTP_REFERER", "/admin/notifications/apikey/"),
        )


@admin.register(Bot)
class BotAdmin(ModelAdmin):
    list_display = ("name", "owner", "bot_actions")
    inlines = [APIKeyInline]

    def bot_actions(self, obj):
        """Добавляет кнопку для генерации нового API-ключа."""
        return format_html(
            '<a class="button" href="generate_key/{}/">Сгенерировать API-ключ</a>',
            obj.id,
        )

    bot_actions.short_description = "Действия"

    def get_urls(self):
        """Добавляет кастомные URL в админку."""
        custom_urls = [
            path("generate_key/<int:bot_id>/", self.generate_key),
        ]
        return custom_urls + super().get_urls()

    def generate_key(self, request, bot_id):
        """Генерация нового API-ключа."""
        bot = get_object_or_404(Bot, id=bot_id)
        api_key = bot.generate_api_key()
        messages.success(
            request,
            f"Создан новый API-ключ: {api_key.key[:10]}...",
        )
        return redirect(
            request.META.get("HTTP_REFERER", "/admin/notifications/bot/"),
        )
