from modeltranslation.translator import register, TranslationOptions
from .apps.bot.models import Text


@register(Text)
class TextTranslationOptions(TranslationOptions):
    fields = 'text',
