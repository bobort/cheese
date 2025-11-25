import datetime

from django.template.defaulttags import csrf_token
from django.utils.html import escape
from django.utils.text import slugify
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe
from jinja2 import Environment
from compressor.contrib.jinja2ext import CompressorExtension
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage

# Import utils.jinja2_filters to ensure decorators are registered
import utils.jinja2_filters  # noqa

def static(path):
    """Django static file URL helper for Jinja2."""
    # Remove leading slash if present, as staticfiles_storage.url handles it
    path = path.lstrip('/')
    return staticfiles_storage.url(path)


def environment(**options):
    """Custom Jinja2 environment using django-jinja."""
    # Create standard Jinja2 environment
    env = Environment(**options)
    
    # Add compressor extension
    env.add_extension(CompressorExtension)
    
    # Add custom globals including the static function
    env.globals.update({
        'static': static,
        'url': reverse,
        'this_year': datetime.date.today().year,
        'csrf_token': csrf_token,
        'escape': escape,
        'slugify': slugify,
    })
    
    return env