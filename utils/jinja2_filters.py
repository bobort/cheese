"""
Jinja2 filter functions for custom template tags
"""
from datetime import timedelta
import locale
import platform
from os import urandom

from django_jinja import library
from django_jinja import jinja2


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


def environment(**options):
    """Custom Jinja2 environment."""
    env = jinja2.get_default_environment(**options)
    return env
