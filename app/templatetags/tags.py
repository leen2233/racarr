from django import template
import json

register = template.Library()

@register.filter
def format_genres(value):
    return ", ".join(value)

@register.filter
def stringify(value):
    return json.dumps(value)

@register.filter
def get_downloaded_width(value):
    return 100 / value.total_count * value.downloaded_count

