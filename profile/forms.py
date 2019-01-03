from crispy_forms.layout import Layout, Field, Div
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from profile.models import Student, Payment
from utils.views import CrispyFormMixin


class StudentCreationForm(CrispyFormMixin, UserCreationForm):
    agree_to_terms = forms.BooleanField(label="I agree to the <a href='/legal/terms' target='_blank'>terms of use</a>.")

    layout = Layout(
        Div(Div(Field('email'), css_class="col"), css_class="row"),
        Div(Div(Field('password1'), css_class="col"), css_class="row"),
        Div(Div(Field('password2'), css_class="col"), css_class="row"),
        Div(
            Div(Field('first_name'), css_class="col"),
            Div(Field('last_name'), css_class="col"),
            css_class="row"
        ),
        Div(
            Div(Field('phone_number'), css_class="col"),
            Div(Field('graduation_year'), css_class="col"),
            Div(Field('degree'), css_class="col"),
            css_class="row",
        ),
        Div(
            Div(Field('exam'), css_class="col"),
            Div(Field('test_date'), css_class="col"),
            css_class="row"
        ),
        Div(
            Div(Field('agree_to_terms'), css_class="col"),
            css_class="row"
        )
    )

    class Meta:
        model = Student
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'graduation_year', 'degree', 'exam', 'test_date',)
        field_classes = {'email': forms.EmailField}

    def clean_agree_to_terms(self):
        if not self.cleaned_data.get('agree_to_terms'):
            return forms.ValidationError('You must agree to the terms of use before registering.')
        return True


class StudentChangeForm(CrispyFormMixin, UserChangeForm):
    layout = Layout(
        Div(Div(Field('email'), css_class="col"), css_class="row"),
        Div(
            Div(Field('first_name'), css_class="col"),
            Div(Field('last_name'), css_class="col"),
            css_class="row"
        ),
        Div(
            Div(Field('phone_number'), css_class="col"),
            Div(Field('graduation_year'), css_class="col"),
            Div(Field('degree'), css_class="col"),
            css_class="row",
        ),
        Div(
            Div(Field('exam'), css_class="col"),
            Div(Field('test_date'), css_class="col"),
            css_class="row"
        ),
    )

    class Meta:
        model = Student
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'graduation_year', 'degree', 'exam', 'test_date',)
        field_classes = {'email': forms.EmailField}


class PaymentForm(CrispyFormMixin, forms.ModelForm):
    in_person_charge = forms.DecimalField(initial=60, decimal_places=2, disabled=True, label="In person charge (USD)")
    remote_charge = forms.DecimalField(initial=75, decimal_places=2, disabled=True, label="Remote charge (USD)")

    class Meta:
        model = Payment
        fields = ('in_person_appt_qty', 'remote_appt_qty')

    layout = Layout(
        Div(
            Div(Field('in_person_appt_qty'), css_class="col"),
            Div(Field('in_person_charge'), css_class="col"),
            css_class="row"
        ),
        Div(
            Div(Field('remote_appt_qty'), css_class="col"),
            Div(Field('remote_charge'), css_class="col"),
            css_class="row"
        )
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    @property
    def total(self):
        return (
            self.cleaned_data.get('in_person_appt_qty') * self.cleaned_data.get('in_person_charge') +
            self.cleaned_data.get('remote_appt_qty') * self.cleaned_data.get('remote_charge')
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.student = self.user
        instance.total = self.total
        if commit:
            instance.save()
        return instance
