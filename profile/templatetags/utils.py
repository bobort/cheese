import locale
import platform

from django import template

register = template.Library()


@register.filter
def currency(value):
    system = platform.system()  # to get the platform you are using.
    if system == 'Darwin':  # Darwin has different naming
        locale.setlocale(locale.LC_ALL, 'EN_US')  # Default us english on Darwin
    else:  # system isn't Darwin
        locale.setlocale(locale.LC_ALL, '')  # this works for Windows and Debian
    return locale.currency(value or 0, grouping=True)
