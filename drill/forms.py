from django import forms
from tinymce.models import HTMLField

from drill.models import DrillTopic


class ConvertDrillForm(forms.Form):
    title = forms.CharField(max_length=255)
    convert_block = HTMLField()

    def save(self):
        drill_name = DrillTopic.objects.get_or_create(name=self.cleaned_data['title'])[0]
        # TODO Complete conversion alrogithm
        raise NotImplementedError
