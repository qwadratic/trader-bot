from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from bot.models import Text, CurrencyList


@admin.register(Text)
class TextAdmin(TranslationAdmin):
    list_display = 'name',


@admin.register(CurrencyList)
class TextAdmin(admin.ModelAdmin):
    list_display = ('currency', 'accuracy', 'type')
