import locale

from django import template

register = template.Library()


@register.filter
def currency(value):
    locale.setlocale(locale.LC_ALL, 'English_United States.1252' )
    return locale.currency(value, grouping=True)
