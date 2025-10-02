from django import template

register = template.Library()

@register.filter
def chr_filter(value, offset=64):
    """
    Convert a number to its corresponding character.
    Default offset is 64, so 1 becomes 'A', 2 becomes 'B', etc.
    """
    try:
        return chr(int(value) + int(offset))
    except (ValueError, TypeError):
        return ''