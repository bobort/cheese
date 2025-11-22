from crispy_forms.layout import Layout, Field, Div, HTML, Row, Column, Fieldset
from django import forms
from django.forms import inlineformset_factory, formset_factory
from tinymce.widgets import TinyMCE

from profile.models import Student, Product
from staff.models import Proposal, ProposalLineItem, ProposalComment, ProposalPaymentPlan, ProposalRevision


class ProposalForm(forms.ModelForm):
    """Form for creating/editing proposals"""
    
    class Meta:
        model = Proposal
        fields = [
            'student', 'title', 'introduction', 'terms_and_conditions', 
            'notes', 'expires_at', 'has_payment_plan', 'payment_plan_months',
            'payment_plan_start_date'
        ]
        widgets = {
            'introduction': TinyMCE(attrs={'cols': 80, 'rows': 10}),
            'terms_and_conditions': TinyMCE(attrs={'cols': 80, 'rows': 10}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'expires_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'payment_plan_start_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_staff=False).order_by('last_name', 'first_name')
        self.fields['expires_at'].required = False
        self.fields['payment_plan_start_date'].required = False


class ProposalLineItemForm(forms.ModelForm):
    """Form for proposal line items"""
    
    class Meta:
        model = ProposalLineItem
        fields = ['product', 'description', 'quantity', 'price', 'notes', 'start_date', 'end_date']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(removed=False)
        self.fields['product'].required = False
        self.fields['description'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        description = cleaned_data.get('description')
        
        if not product and not description:
            raise forms.ValidationError("Either a product or description must be provided.")
        
        return cleaned_data


ProposalLineItemFormSet = inlineformset_factory(
    Proposal,
    ProposalLineItem,
    form=ProposalLineItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class ProposalCommentForm(forms.ModelForm):
    """Form for adding comments to proposals"""
    
    class Meta:
        model = ProposalComment
        fields = ['comment', 'is_internal']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        comment = super().save(commit=False)
        if self.user:
            comment.author = self.user
            comment.author_type = 'staff' if self.user.is_staff else 'student'
        if commit:
            comment.save()
        return comment


class ProposalPaymentPlanForm(forms.ModelForm):
    """Form for creating/editing payment plans"""
    
    class Meta:
        model = ProposalPaymentPlan
        fields = [
            'number_of_payments', 'payment_frequency', 'first_payment_date',
            'first_payment_amount', 'regular_payment_amount'
        ]
        widgets = {
            'first_payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_payment_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'regular_payment_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'number_of_payments': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'payment_frequency': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.proposal = kwargs.pop('proposal', None)
        super().__init__(*args, **kwargs)
        if self.proposal:
            self.fields['first_payment_amount'].required = False
    
    def clean(self):
        from decimal import Decimal
        cleaned_data = super().clean()
        number_of_payments = cleaned_data.get('number_of_payments', 1)
        first_payment_amount = cleaned_data.get('first_payment_amount')
        regular_payment_amount = cleaned_data.get('regular_payment_amount')
        
        if self.proposal:
            total = self.proposal.total_amount
            if first_payment_amount and regular_payment_amount:
                calculated_total = Decimal(str(first_payment_amount)) + (Decimal(str(regular_payment_amount)) * (number_of_payments - 1))
                if abs(calculated_total - total) > Decimal('0.01'):
                    raise forms.ValidationError(
                        f"Payment amounts don't match proposal total. "
                        f"Expected: ${total}, Calculated: ${calculated_total}"
                    )
        
        return cleaned_data


class ProposalRevisionForm(forms.ModelForm):
    """Form for creating proposal revisions"""
    
    class Meta:
        model = ProposalRevision
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

