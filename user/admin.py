from django.contrib import admin

from user.models import TelegramUser


@admin.register(TelegramUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'telegram_id', 'username', 'first_name', 'last_name', 'last_activity', 'created_at')

