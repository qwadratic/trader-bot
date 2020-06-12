from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from .models import Text
import trader_bot.translation


@admin.register(Text)
class TextAdmin(TranslationAdmin):

    list_display = ('text',)