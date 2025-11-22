from decimal import Decimal
from django.db import models
from django.db.models import Sum, F
from django.urls import reverse
from django.utils import timezone
from tinymce.models import HTMLField

from profile.models import Student, Product


class IndependentContractorTerms(models.Model):
    """Terms document for independent contractors to sign"""
    document = HTMLField(help_text="Terms and conditions document")
    date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ('-date',)
        verbose_name = 'Independent Contractor Terms'
        verbose_name_plural = 'Independent Contractor Terms'
    
    def __str__(self):
        return f"Terms dated {self.date}"


class ElectronicSignature(models.Model):
    """Electronic signature for independent contractor terms"""
    document = models.ForeignKey(IndependentContractorTerms, on_delete=models.CASCADE, related_name='signatures')
    staff_member = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='electronic_signatures')
    date = models.DateField()
    initials = models.CharField(max_length=5, help_text="Staff member's initials")
    
    class Meta:
        ordering = ('-date',)
        unique_together = ('document', 'staff_member')
        verbose_name = 'Electronic Signature'
        verbose_name_plural = 'Electronic Signatures'
    
    def __str__(self):
        return f"{self.staff_member} - {self.document.date} ({self.initials})"


class Proposal(models.Model):
    """Proposal sent to students for services"""
    DRAFT = 'draft'
    SENT = 'sent'
    REVIEWED = 'reviewed'
    REVISED = 'revised'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    EXPIRED = 'expired'
    
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (SENT, 'Sent'),
        (REVIEWED, 'Reviewed by Student'),
        (REVISED, 'Revised'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (EXPIRED, 'Expired'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='proposals')
    created_by = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='proposals_created')
    proposal_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    
    # Proposal details
    title = models.CharField(max_length=255, default="Tutoring Services Proposal")
    introduction = HTMLField(blank=True, null=True, help_text="Introduction/cover letter text")
    terms_and_conditions = HTMLField(blank=True, null=True, help_text="Terms and conditions")
    notes = models.TextField(blank=True, null=True, help_text="Internal notes (not visible to student)")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    
    # Payment plan
    has_payment_plan = models.BooleanField(default=False)
    payment_plan_months = models.IntegerField(default=1, help_text="Number of months for payment plan")
    payment_plan_start_date = models.DateField(blank=True, null=True)
    
    # Stripe integration
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_active = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self):
        return f"Proposal {self.proposal_number} - {self.student} ({self.get_status_display()})"
    
    def get_absolute_url(self):
        return reverse('staff:proposal-detail', kwargs={'pk': self.pk})
    
    @classmethod
    def get_next_number(cls):
        current_year = timezone.now().year
        proposals_this_year = cls.objects.filter(created_at__year=current_year).count() or 0
        return f"PROP-{str(current_year)[2:]}-{(proposals_this_year + 1):04d}"
    
    @property
    def total_amount(self):
        """Calculate total amount from line items"""
        return self.proposallineitem_set.aggregate(
            s=Sum(F('price') * F('quantity'), output_field=models.FloatField())
        )['s'] or Decimal('0.00')
    
    @property
    def monthly_payment(self):
        """Calculate monthly payment amount"""
        if self.has_payment_plan and self.payment_plan_months > 0:
            return self.total_amount / Decimal(self.payment_plan_months)
        return self.total_amount
    
    def save(self, *args, **kwargs):
        if not self.proposal_number:
            self.proposal_number = Proposal.get_next_number()
        super().save(*args, **kwargs)


class ProposalLineItem(models.Model):
    """Individual items/services in a proposal"""
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='proposallineitem_set')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255, help_text="Item description")
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about this item")
    
    # Optional dates for service period
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    class Meta:
        ordering = ('id',)
    
    def __str__(self):
        return f"{self.description} x{self.quantity} @ ${self.price}"
    
    @property
    def line_total(self):
        return Decimal(self.quantity) * self.price


class ProposalRevision(models.Model):
    """Track revisions/changes to proposals"""
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='revisions')
    revised_by = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='proposal_revisions')
    revision_number = models.IntegerField(default=1)
    notes = models.TextField(help_text="What changed in this revision")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-revision_number',)
        unique_together = ('proposal', 'revision_number')
    
    def __str__(self):
        return f"Revision {self.revision_number} of {self.proposal.proposal_number}"


class ProposalComment(models.Model):
    """Comments/feedback on proposals from students and staff"""
    STUDENT = 'student'
    STAFF = 'staff'
    
    AUTHOR_TYPE_CHOICES = [
        (STUDENT, 'Student'),
        (STAFF, 'Staff'),
    ]
    
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    author_type = models.CharField(max_length=10, choices=AUTHOR_TYPE_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=False, help_text="Internal notes (not visible to student)")
    
    class Meta:
        ordering = ('created_at',)
    
    def __str__(self):
        return f"Comment on {self.proposal.proposal_number} by {self.author_type}"


class ProposalPaymentPlan(models.Model):
    """Custom payment plan details for proposals"""
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE, related_name='payment_plan')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_payments = models.IntegerField(default=1)
    payment_frequency = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('biweekly', 'Bi-weekly'),
            ('weekly', 'Weekly'),
            ('custom', 'Custom'),
        ],
        default='monthly'
    )
    first_payment_date = models.DateField()
    first_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    regular_payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Stripe subscription details
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment plan for {self.proposal.proposal_number}"
    
    @property
    def subscription_active(self):
        """Get subscription_active status from the related Proposal"""
        return self.proposal.subscription_active if self.proposal else False
