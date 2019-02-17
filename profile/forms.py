from crispy_forms.layout import Layout, Field, Div
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from profile.models import Student, Order, Product, OrderLineItem
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
                form=OrderLineItemForm, extra=len(self.initial_formset_data)
            )(self.data or None, instance=self.instance, initial=self.initial_formset_data)
        return self._formset

    def is_valid(self):
        return self.formset.is_valid() and super().is_valid()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.student = self.user
        if commit:
            self.instance = instance.save()
            self.formset.save()
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
