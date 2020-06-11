from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    last_display = ('id', 'telegram_id', 'username', 'first_name', 'last_name', 'last_activity', 'date_reg')
