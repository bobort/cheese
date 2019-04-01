from crispy_forms.layout import Layout, Div, Field
from django import forms

from profile.models import GroupSession
from utils.views import CrispyFormMixin


class GroupSessionAppointmentForm(CrispyFormMixin, forms.ModelForm):
    layout = Layout(
        Div(Field('occurrence', hidden=True)),  # handled by the template
        Div(Field('zoom_id'), css_class="col-4 field-zoom-id"),
    )

    class Meta:
        model = GroupSession
        fields = ['occurrence', 'zoom_id']
