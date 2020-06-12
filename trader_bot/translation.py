from modeltranslation.translator import register, TranslationOptions, translator
from .apps.bot.models import Text


@register(Text)
class TextTranslationOptions(TranslationOptions):
    fields = ('text',)