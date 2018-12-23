from crispy_forms.layout import Layout, Field, Div
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField

from profile.models import Student
from utils.views import CrispyFormMixin


class StudentForm(CrispyFormMixin, forms.ModelForm):
    layout = Layout(
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
        fields = ('phone_number', 'graduation_year', 'degree', 'exam', 'test_date',)


class UserForm(CrispyFormMixin, UserCreationForm):
    """
    https://docs.djangoproject.com/en/2.1/ref/contrib/auth/#fields
    """
    username = forms.EmailField(label="Email address")
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)

    layout = Layout(
        Div(
            Div(Field('first_name'), css_class="col"),
            Div(Field('last_name'), css_class="col"),
            css_class="row"
        ),
        Div(Div(Field('username'), css_class="col"), css_class="row"),
        Div(Div(Field('password1'), css_class="col"), css_class="row"),
        Div(Div(Field('password2'), css_class="col"), css_class="row"),
    )

    def save(self, commit=True):
        user = super().save(commit)
        user.email = self.cleaned_data.get('username')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        if commit:
            user.save()
        return user
