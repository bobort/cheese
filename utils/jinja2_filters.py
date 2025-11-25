"""
Jinja2 filter functions for custom template tags
"""
from datetime import timedelta
import locale
import platform
from os import urandom

from django_jinja import library
from django_jinja import jinja2
from django.contrib.staticfiles.storage import staticfiles_storage


@library.filter
def minutes_ago(dt, minutes):
    """Returns datetime that is number of minutes before that datetime."""
    return dt - timedelta(minutes=minutes)


@library.filter
def currency(value):
    """Format value as currency."""
    system = platform.system()
    if system == 'Darwin':
        locale.setlocale(locale.LC_ALL, 'EN_US')
    else:
        locale.setlocale(locale.LC_ALL, '')
    return locale.currency(value or 0, grouping=True)


@library.filter
def has_group(user, group_name):
    """Check if user belongs to a group."""
    return user.groups.filter(name=group_name).exists()


@library.filter
def encrypt(s, key=None):
    """XOR encrypt a string."""
    s = str(s)
    if key is None:
        key = len(s)
    return "".join(chr(ord(a) ^ (key % 255)) for a in s)


@library.global_function
def static(path):
    """Django static file URL helper for Jinja2."""
    # Remove leading slash if present, as staticfiles_storage.url handles it
    path = path.lstrip('/')
    return staticfiles_storage.url(path)


@library.global_function
def crispy(form):
    """Render a crispy form in Jinja2."""
    from crispy_forms.utils import render_crispy_form
    return render_crispy_form(form)


@library.filter
def as_crispy_errors(form):
    """Render crispy form errors."""
    from crispy_forms.utils import render_crispy_form
    return render_crispy_form(form)


@library.filter
def crispy_filter(form):
    """Render a crispy form as a filter."""
    from crispy_forms.utils import render_crispy_form
    return render_crispy_form(form)


@library.filter
def bootstrap(form):
    """Render a Django form with Bootstrap 5 styling."""
    from django.forms import BaseForm
    from django.utils.safestring import mark_safe
    
    if not isinstance(form, BaseForm):
        return ""
    
    html_parts = []
    for field in form:
        field_html = []
        field_html.append(f'<div class="mb-3">')
        
        # Label
        if field.label:
            field_html.append(f'<label for="{field.id_for_label}" class="form-label">{field.label}')
            if field.field.required:
                field_html.append('<span class="text-danger">*</span>')
            field_html.append('</label>')
        
        # Field
        field_html.append(str(field))
        
        # Help text
        if field.help_text:
            field_html.append(f'<div class="form-text">{field.help_text}</div>')
        
        # Errors
        if field.errors:
            field_html.append('<div class="invalid-feedback d-block">')
            for error in field.errors:
                field_html.append(f'<div>{error}</div>')
            field_html.append('</div>')
        
        field_html.append('</div>')
        html_parts.append(''.join(field_html))
    
    # Non-field errors
    if form.non_field_errors():
        html_parts.insert(0, '<div class="alert alert-danger" role="alert">')
        for error in form.non_field_errors():
            html_parts.insert(1, f'<div>{error}</div>')
        html_parts.insert(2, '</div>')
    
    return mark_safe(''.join(html_parts))




def environment(**options):
    """Custom Jinja2 environment."""
    env = jinja2.get_default_environment(**options)
    return env
