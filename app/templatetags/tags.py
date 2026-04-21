from django import template

register = template.Library()

@register.filter
def format_genres(value):
    return ", ".join(value)

