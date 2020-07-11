from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from bot.models import Text


@admin.register(Text)
class TextAdmin(TranslationAdmin):
    list_display = 'name',
