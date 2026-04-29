from django import template
import json

register = template.Library()

@register.filter
def format_genres(value):
    return ", ".join(value)

@register.filter
def stringify(value):
    return json.dumps(value)

