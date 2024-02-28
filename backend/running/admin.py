from django.contrib.admin import ModelAdmin, register

from .models import MotivationalPhrase, RecreationPhrase


@register(MotivationalPhrase)
class MotivationalPhraseAdmin(ModelAdmin):
	list_display = ("text",)


@register(RecreationPhrase)
class RecreationPhraseAdmin(ModelAdmin):
	list_display = ("text",)
