"""
Custom context processors for Jinja2 templates.
"""
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe


def csrf_input(request):
    """Add csrf_input to template context."""
    if request:
        token = get_token(request)
        return {
            'csrf_input': mark_safe(f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">')
        }
    return {
        'csrf_input': mark_safe('<input type="hidden" name="csrfmiddlewaretoken" value="">')
    }

