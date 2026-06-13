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

@register.filter
def format_size(num_bytes):
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024

    if num_bytes >= GB:
        return f"{num_bytes / GB:.2f} GB"
    elif num_bytes >= MB:
        return f"{num_bytes / MB:.2f} MB"
    elif num_bytes >= KB:
        return f"{num_bytes / KB:.2f} KB"
    else:
        return f"{num_bytes} bytes"
