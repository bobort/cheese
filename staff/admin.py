from django.contrib import admin

from staff.models import (
    ElectronicSignature, IndependentContractorTerms,
    Proposal, ProposalLineItem, ProposalComment, ProposalRevision, ProposalPaymentPlan
)


class ProposalLineItemInline(admin.TabularInline):
    model = ProposalLineItem
    extra = 1


class ProposalCommentInline(admin.TabularInline):
    model = ProposalComment
    extra = 0
    readonly_fields = ('author', 'author_type', 'created_at')
    fields = ('author', 'author_type', 'comment', 'is_internal', 'created_at')


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('proposal_number', 'student', 'status', 'total_amount', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at', 'has_payment_plan')
    search_fields = ('proposal_number', 'student__first_name', 'student__last_name', 'student__email')
    readonly_fields = ('proposal_number', 'created_at', 'sent_at', 'accepted_at')
    inlines = [ProposalLineItemInline, ProposalCommentInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('proposal_number', 'student', 'created_by', 'status', 'title')
        }),
        ('Content', {
            'fields': ('introduction', 'terms_and_conditions', 'notes')
        }),
        ('Payment Plan', {
            'fields': ('has_payment_plan', 'payment_plan_months', 'payment_plan_start_date',
                      'stripe_subscription_id', 'subscription_active')
        }),
        ('Dates', {
            'fields': ('created_at', 'sent_at', 'expires_at', 'accepted_at')
        }),
    )


@admin.register(ProposalLineItem)
class ProposalLineItemAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'description', 'quantity', 'price', 'line_total')
    list_filter = ('proposal__status',)
    search_fields = ('proposal__proposal_number', 'description', 'product__name')


@admin.register(ProposalComment)
class ProposalCommentAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'author', 'author_type', 'created_at', 'is_internal')
    list_filter = ('author_type', 'is_internal', 'created_at')
    search_fields = ('proposal__proposal_number', 'comment', 'author__email')


@admin.register(ProposalRevision)
class ProposalRevisionAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'revision_number', 'revised_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('proposal__proposal_number', 'notes')


@admin.register(ProposalPaymentPlan)
class ProposalPaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'total_amount', 'number_of_payments', 'payment_frequency', 'subscription_active')
    list_filter = ('payment_frequency', 'created_at')
    search_fields = ('proposal__proposal_number',)

admin.site.register(ElectronicSignature)
admin.site.register(IndependentContractorTerms)


