import locale
import platform
from datetime import timedelta
from os import urandom

from django import template

register = template.Library()


@register.filter
def minutes_ago(dt, minutes):
    """ Returns datetime that is number of minutes before that datetime."""
    return dt - timedelta(minutes=minutes)


@register.filter
def currency(value):
    system = platform.system()  # to get the platform you are using.
    if system == 'Darwin':  # Darwin has different naming
        locale.setlocale(locale.LC_ALL, 'EN_US')  # Default us english on Darwin
    else:  # system isn't Darwin
        locale.setlocale(locale.LC_ALL, '')  # this works for Windows and Debian
    return locale.currency(value or 0, grouping=True)


@register.filter
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def encrypt(s, key=None):
    if key is None:
        key = len(s)
    return "".join(chr(ord(a) ^ (key % 255)) for a in s)
