from django.contrib import admin
from django import forms

from drill.models import DrillTopic, Question


def process_qa(topic, qas):
    """ The qas string is delimited as so:
    The first line is 5 pipes: |||||
    After that is the question followed by |~|~|
    Followed by the answer
    """
    lines = qas.split("\r\n")
    Q_MODE = False
    text = ""
    question = Question(topic=topic)
    for line in lines:
        if line == "|||||":
            Q_MODE = True
            if question.q:
                question.a = f"<ul>{text}</ul>"
                question.save()
                question = Question(topic=topic)
                text = ""
        elif line == "|~|~|":
            Q_MODE = False
            question.q = text
            text = ""
        else:
            if not Q_MODE and line:
                text += f"<li>{line}</li>"
            else:
                text += line


class DrillModelForm(forms.ModelForm):
    qa_parser = forms.CharField(widget=forms.Textarea, required=False, label="QA Parser")

    def _save_m2m(self):
        super()._save_m2m()
        parse = self.cleaned_data.get('qa_parser')
        if parse:
            process_qa(self.instance, parse)

    class Meta:
        model = DrillTopic
        fields = ('name', )


class DrillAdmin(admin.ModelAdmin):
    model = DrillTopic
    form = DrillModelForm
    search_fields = ('name', )
    ordering = ('name',)


admin.site.register(DrillTopic, DrillAdmin)
admin.site.register(Question)
