from django import template

register = template.Library()

@register.filter
def get_item(mapping, key):
    """Dict lookup by a variable key — Django's dot-lookup only supports
    literal keys, so a question's dynamic id needs this to read its current
    answer out of the `answers` dict when pre-filling the edit form."""
    if not mapping:
        return ""
    return mapping.get(str(key), "")
