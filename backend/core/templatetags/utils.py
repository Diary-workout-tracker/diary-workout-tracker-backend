from django import template

register = template.Library()


@register.filter
def get_type(value):
	"""Отдаёт тип."""
	return type(value).__name__
