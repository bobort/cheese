"""
Utility models and mixins
"""
from django.db import models


class HTMLMixin(models.Model):
    """Mixin for models that need HTML field support"""
    
    class Meta:
        abstract = True

