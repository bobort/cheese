from crispy_forms.layout import Layout, Field, Div
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.core.mail import send_mail
from django.template.loader import render_to_string

from profile.models import Student, Order, Product, OrderLineItem
from utils import send_html_email
from utils.views import CrispyFormMixin


class StudentCreationForm(CrispyFormMixin, UserCreationForm):
    agree_to_terms = forms.BooleanField(
        label="I agree to the <a href='/legal/terms' target='_blank'>terms of use</a>."
    )

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
            Div(Field('marketing_subscription'), css_class="col"),
            css_class="row"
        ),
        Div(
            Div(Field('agree_to_terms'), css_class="col"),
            css_class="row"
        )
    )

    class Meta:
        model = Student
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'graduation_year',
                  'degree', 'exam', 'test_date', 'marketing_subscription')
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
        Div(
            Div(Field('marketing_subscription'), css_class="col"),
            css_class="row"
        ),

    )

    class Meta:
        model = Student
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'graduation_year',
                  'degree', 'exam', 'test_date', 'marketing_subscription')
        field_classes = {'email': forms.EmailField}


class OrderForm(CrispyFormMixin, forms.ModelForm):
    _formset = None

    class Meta:
        model = Order
        fields = ()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    @property
    def initial_formset_data(self):
        initial_data = []
        for product in Product.objects.all():
            initial_data.append({
                'product': product,
                'qty': 0,
                'charge': product.charge,
            })
        return initial_data

    @property
    def formset(self):
        if not self._formset:
            self._formset = forms.inlineformset_factory(
                Order, OrderLineItem,
                form=OrderLineItemForm, formset=OrderLineItemFormSet, extra=len(self.initial_formset_data)
            )(self.data or None, instance=self.instance, initial=self.initial_formset_data)
        return self._formset

    def is_valid(self):
        return self.formset.is_valid() and super().is_valid()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.student = self.user
        if commit:
            instance.save()
            self.formset.save()
            # send email message after everything is saved
            message = render_to_string('email_receipt.html', {'order': instance})
            send_html_email(
                "New Payment", message, ["matthew.pava@gmail.com", "drlepava@gmail.com"], [instance.student.email]
            )
            send_html_email(
                "Thank you for your payment.", message, [instance.student.email], "matthew.pava@gmail.com"
            )
        return instance


class OrderLineItemForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = OrderLineItem
        fields = ('product', 'qty', 'charge')

    layout = Layout(
        Div(
            Div(
                Field('product', readonly=True, css_class="d-none"),  # javascript takes care of product rendering
                css_class="col-xs-12 col-6 field-product"
            ),
            Div(Field('qty'), css_class="col-xs-6 col-3 field-qty"),
            Div(
                Field('charge', readonly=True, css_class="readonly disabled form-control-plaintext"),
                css_class="col-xs-6 col-3 field-money"
            ),
            css_class="row formset-item"
        ),
    )

    def clean(self):
        super().clean()
        if self.cleaned_data:
            product = self.cleaned_data.get('product')
            qty = self.cleaned_data.get('qty', 0)
            charge = self.cleaned_data.get('charge', -1)
            if product and product.charge != charge:  # server-side validation in case fields are modified on client
                raise forms.ValidationError({'charge': "Invalid charge for product. Please refresh the page."})
            if qty == 0:
                self.cleaned_data['DELETE'] = True
        return self.cleaned_data


class OrderLineItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        result = super().clean()
        # make sure we have at least one qty filled out in the formset
        qty_0 = 0
        for form in self.forms:
            if (form.cleaned_data.get('qty') or 0) == 0:
                qty_0 += 1
        if qty_0 == len(self.forms):
            raise forms.ValidationError("You must have a quantity of at least one on this page.")
        return result

