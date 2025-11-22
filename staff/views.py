"""
Staff views for managing students, orders, and account balances
Uses HTMX for dynamic updates
"""
from decimal import Decimal
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import FieldError, PermissionDenied
from django.db.models import Case, When, Max, F, Q, IntegerField, Sum, Count
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.base import TemplateView, RedirectView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect

from profile.models import Student, OrderLineItem, Order, StripePayment
from staff.models import ElectronicSignature, IndependentContractorTerms, Proposal, ProposalLineItem, ProposalComment, ProposalRevision, ProposalPaymentPlan
from staff.forms import ProposalForm, ProposalLineItemFormSet, ProposalCommentForm, ProposalPaymentPlanForm, ProposalRevisionForm
from utils import divide_chunks
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import UpdateView
from django.views.decorators.http import require_POST
from django.db import transaction


class IndexView(RedirectView):
    """Redirect to appropriate staff dashboard based on user group"""
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.groups.filter(name="oceancouragegroup").exists():
            return reverse("staff:ocean-courage-list")
        elif self.request.user.groups.filter(name="instructorgroup").exists() or self.request.user.is_superuser:
            return reverse("staff:dashboard")
        raise PermissionDenied


class StaffDashboardView(PermissionRequiredMixin, TemplateView):
    """Main staff dashboard with account balance overview"""
    template_name = "staff/dashboard.html"
    permission_required = ['profile.view_student']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all students
        students = Student.objects.filter(is_staff=False)
        
        # Calculate statistics
        total_students = students.count()
        students_with_balance = students.filter(balance_paid=False).count()
        total_outstanding_balance = sum(
            s.account_balance for s in students.filter(balance_paid=False)
            if s.account_balance > 0
        )
        
        # Recent registrations (last 30 days)
        recent_students = students.filter(
            date_joined__gte=timezone.now().date() - timezone.timedelta(days=30)
        ).order_by('-date_joined')[:10]
        
        # Students with highest balances
        high_balance_students = students.filter(
            balance_paid=False,
            account_balance__gt=0
        ).order_by('-account_balance')[:10]
        
        # Recent orders
        recent_orders = Order.objects.all().order_by('-date_paid')[:10]
        
        # Active subscriptions
        active_subscriptions = students.filter(subscription_active=True).count()
        
        context.update({
            'total_students': total_students,
            'students_with_balance': students_with_balance,
            'total_outstanding_balance': total_outstanding_balance,
            'recent_students': recent_students,
            'high_balance_students': high_balance_students,
            'recent_orders': recent_orders,
            'active_subscriptions': active_subscriptions,
        })
        return context


class StudentListView(PermissionRequiredMixin, ListView):
    """List all students with balance information and HTMX filtering"""
    model = Student
    template_name = "staff/student_list.html"
    permission_required = ['profile.view_student']
    paginate_by = 50

    def get_queryset(self):
        order_by = self.request.GET.get('ordering', '-date_joined')
        filter_balance = self.request.GET.get("balance_filter", "all")
        search_query = self.request.GET.get("search", "")
        
        q = super().get_queryset().filter(is_staff=False)
        
        # Search filter
        if search_query:
            q = q.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )
        
        # Balance filter
        if filter_balance == "with_balance":
            q = q.filter(balance_paid=False, account_balance__gt=0)
        elif filter_balance == "paid":
            q = q.filter(balance_paid=True)
        elif filter_balance == "subscription":
            q = q.filter(subscription_active=True)
        
        # Ordering
        if order_by:
            try:
                if order_by.startswith('-'):
                    q = q.order_by(order_by)
                else:
                    q = q.order_by(order_by)
            except FieldError:
                q = q.order_by('-date_joined')
        else:
            q = q.order_by('-date_joined')
        
        return q

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['marketing_list_chunks'] = divide_chunks(
            self.get_queryset().filter(marketing_subscription=True), 90
        )
        context['balance_filter'] = self.request.GET.get("balance_filter", "all")
        context['search_query'] = self.request.GET.get("search", "")
        return context


class StudentDetailView(PermissionRequiredMixin, DetailView):
    """Detailed view of a student with balance and payment history"""
    model = Student
    template_name = "staff/student_detail.html"
    permission_required = ['profile.view_student']
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        
        # Get payment history
        orders = Order.objects.filter(student=student).order_by('-date_paid')
        stripe_payments = StripePayment.objects.filter(
            student=student,
            status='succeeded'
        ).order_by('-created_at')
        
        # Calculate balance breakdown
        student.update_account_balance()  # Refresh balance
        
        # Calculate totals
        total_owed = sum(o.grand_total for o in orders) or Decimal('0.00')
        total_paid_orders = sum(o.grand_total for o in orders if o.date_paid) or Decimal('0.00')
        total_paid_stripe = sum(p.amount for p in stripe_payments) or Decimal('0.00')
        total_paid = total_paid_orders + total_paid_stripe
        remaining_balance = total_owed - total_paid
        
        # Combine all payments for display
        all_payments = []
        # Add order payments
        for order in orders:
            if order.date_paid:
                all_payments.append({
                    'date': order.date_paid,
                    'amount': order.grand_total,
                    'type': 'Order Payment',
                    'reference': order.number,
                    'method': 'Order',
                })
        # Add Stripe payments
        for payment in stripe_payments:
            all_payments.append({
                'date': payment.paid_at or payment.created_at,
                'amount': payment.amount,
                'type': 'Subscription Payment',
                'reference': payment.stripe_invoice_id or payment.stripe_payment_intent_id,
                'method': 'Stripe',
            })
        # Sort by date descending
        all_payments.sort(key=lambda x: x['date'], reverse=True)
        
        context.update({
            'orders': orders,
            'stripe_payments': stripe_payments,
            'total_orders': orders.count(),
            'total_owed': total_owed,
            'total_paid_orders': total_paid_orders,
            'total_paid_stripe': total_paid_stripe,
            'total_paid': total_paid,
            'remaining_balance': remaining_balance,
            'all_payments': all_payments,
            'subscription_status': 'Active' if student.subscription_active else 'Inactive',
        })
        return context


class OrderLineItemListView(PermissionRequiredMixin, ListView):
    """List all order line items"""
    model = OrderLineItem
    template_name = "staff/orderlineitem_list.html"
    permission_required = ['profile.view_orderlineitem']
    ordering = ('-order__date_paid',)
    paginate_by = 50

    def get_queryset(self):
        order_by = self.request.GET.get('ordering')
        q = super().get_queryset()
        if order_by:
            try:
                q = q.order_by(order_by)
            except FieldError:
                pass
        return q
class OceanCourageSubscribersView(PermissionRequiredMixin, ListView):
    """List Ocean Courage subscribers (legacy view - keeping for compatibility)"""
    model = Student
    template_name = "staff/oceancourage_list.html"

    def has_permission(self):
        return self.request.user.groups.filter(name="oceancouragegroup").exists() or self.request.user.is_superuser

    def get_queryset(self):
        order_by = self.request.GET.get('ordering')
        q = super().get_queryset().filter(
            productuser__product_end_date__gte=timezone.now().date(),
            productuser__product__name="Ocean Courage Drill Sessions"
        ).annotate(
            last_purchase_date=Max('order__date_paid')
        )

        if order_by:
            if 'expiration' in order_by:
                sorted_q = sorted(
                    q, key=lambda d: d.ocean_courage_subscription.expiration if d.ocean_courage_subscription else None,
                    reverse=True if '-expiration' in order_by else False
                )
                cases = [When(pk=record.pk, then=sort_order) for sort_order, record in enumerate(sorted_q)]
                q = q.annotate(sort_order=Case(*cases, output_field=IntegerField())).order_by('sort_order')
            else:
                try:
                    q = q.order_by(order_by)
                except FieldError:
                    pass
        return q


class ThrowError(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Error testing view"""
    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        raise ValueError("Error purposefully generated.")


class SignTerms(PermissionRequiredMixin, CreateView):
    """Sign independent contractor terms"""
    model = ElectronicSignature
    template_name = 'staff/sign_terms.html'
    fields = ['document', 'staff_member', 'date', 'initials']
    success_url = reverse_lazy('frontend:index')

    def has_permission(self):
        return self.request.user.groups.filter(name="oceancouragegroup").exists() or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = IndependentContractorTerms.objects.first()
        context['signature'] = not ElectronicSignature.objects.filter(
            staff_member=self.request.user, document=context['document']
        ).exists()
        return context


# HTMX partial views for dynamic updates
@login_required
@permission_required('profile.view_student', raise_exception=True)
@require_http_methods(["GET"])
def student_balance_partial(request, pk):
    """HTMX partial for student balance information"""
    student = get_object_or_404(Student, pk=pk)
    student.update_account_balance()
    
    return JsonResponse({
        'balance': str(student.account_balance),
        'balance_paid': student.balance_paid,
        'subscription_active': student.subscription_active,
        'subscription_id': student.stripe_subscription_id or '',
    })


# Proposal Views
class ProposalListView(PermissionRequiredMixin, ListView):
    """List all proposals"""
    model = Proposal
    template_name = "staff/proposal_list.html"
    permission_required = ['profile.view_student']
    context_object_name = 'proposals'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Proposal.objects.select_related('student', 'created_by').prefetch_related('proposallineitem_set')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by student
        student_id = self.request.GET.get('student')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(proposal_number__icontains=search) |
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__email__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Proposal.STATUS_CHOICES
        context['students'] = Student.objects.filter(is_staff=False).order_by('last_name', 'first_name')
        return context


class ProposalCreateView(PermissionRequiredMixin, CreateView):
    """Create a new proposal"""
    model = Proposal
    form_class = ProposalForm
    template_name = "staff/proposal_form.html"
    permission_required = ['profile.view_student']
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pre-select student if provided
        student_id = self.request.GET.get('student')
        if student_id:
            kwargs['initial'] = {'student': student_id}
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['lineitems'] = ProposalLineItemFormSet(self.request.POST)
        else:
            context['lineitems'] = ProposalLineItemFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        lineitems = context['lineitems']
        
        with transaction.atomic():
            form.instance.created_by = self.request.user
            self.object = form.save()
            
            if lineitems.is_valid():
                lineitems.instance = self.object
                lineitems.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f"Proposal {self.object.proposal_number} created successfully.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('staff:proposal-detail', kwargs={'pk': self.object.pk})


class ProposalDetailView(PermissionRequiredMixin, DetailView):
    """View proposal details with HTMX interactions"""
    model = Proposal
    template_name = "staff/proposal_detail.html"
    permission_required = ['profile.view_student']
    context_object_name = 'proposal'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proposal = self.get_object()
        
        context['lineitems'] = proposal.proposallineitem_set.all()
        context['comments'] = proposal.comments.filter(is_internal=False)
        context['internal_notes'] = proposal.comments.filter(is_internal=True)
        context['revisions'] = proposal.revisions.all()
        context['comment_form'] = ProposalCommentForm(user=self.request.user)
        context['can_edit'] = proposal.status in [Proposal.DRAFT, Proposal.REVISED]
        context['can_send'] = proposal.status == Proposal.DRAFT
        context['can_revise'] = proposal.status in [Proposal.REVIEWED, Proposal.SENT]
        
        return context


class ProposalUpdateView(PermissionRequiredMixin, UpdateView):
    """Update an existing proposal"""
    model = Proposal
    form_class = ProposalForm
    template_name = "staff/proposal_form.html"
    permission_required = ['profile.view_student']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['lineitems'] = ProposalLineItemFormSet(self.request.POST, instance=self.object)
        else:
            context['lineitems'] = ProposalLineItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        lineitems = context['lineitems']
        
        with transaction.atomic():
            self.object = form.save()
            
            if lineitems.is_valid():
                lineitems.save()
            else:
                return self.form_invalid(form)
        
        messages.success(self.request, f"Proposal {self.object.proposal_number} updated successfully.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('staff:proposal-detail', kwargs={'pk': self.object.pk})


@login_required
@permission_required('profile.view_student', raise_exception=True)
@require_http_methods(["POST"])
def send_proposal_email(request, pk):
    """Send proposal email to student"""
    from utils import send_html_email
    
    proposal = get_object_or_404(Proposal, pk=pk)
    
    if proposal.status != Proposal.DRAFT:
        messages.error(request, "Only draft proposals can be sent.")
        return redirect('staff:proposal-detail', pk=proposal.pk)
    
    # Render proposal email
    html_message = render_to_string('staff/email/proposal_email.html', {
        'proposal': proposal,
        'lineitems': proposal.proposallineitem_set.all(),
    })
    
    # Send email
    send_html_email(
        subject=f"Proposal {proposal.proposal_number} - {proposal.title}",
        html_message=html_message,
        recipients=[proposal.student.email],
    )
    
    # Update proposal status
    proposal.status = Proposal.SENT
    proposal.sent_at = timezone.now()
    proposal.save()
    
    messages.success(request, f"Proposal sent to {proposal.student.email}")
    return redirect('staff:proposal-detail', pk=proposal.pk)


@login_required
@permission_required('profile.view_student', raise_exception=True)
@require_http_methods(["POST"])
def add_proposal_comment(request, pk):
    """Add a comment to a proposal (HTMX)"""
    proposal = get_object_or_404(Proposal, pk=pk)
    form = ProposalCommentForm(request.POST, user=request.user)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.proposal = proposal
        comment.save()
        
        # Return updated comments section
        comments = proposal.comments.filter(is_internal=False)
        html = render_to_string('staff/proposal/_comments.html', {
            'proposal': proposal,
            'comments': comments,
            'comment_form': ProposalCommentForm(user=request.user),
        })
        return HttpResponse(html)
    
    # Return form with errors
    html = render_to_string('staff/proposal/_comment_form.html', {
        'form': form,
    })
    return HttpResponse(html)


@login_required
@permission_required('profile.view_student', raise_exception=True)
@require_http_methods(["POST"])
def create_proposal_revision(request, pk):
    """Create a revision of a proposal"""
    proposal = get_object_or_404(Proposal, pk=pk)
    form = ProposalRevisionForm(request.POST)
    
    if form.is_valid():
        revision = form.save(commit=False)
        revision.proposal = proposal
        revision.revised_by = request.user
        
        # Get next revision number
        last_revision = proposal.revisions.order_by('-revision_number').first()
        revision.revision_number = (last_revision.revision_number + 1) if last_revision else 1
        
        revision.save()
        
        # Update proposal status
        proposal.status = Proposal.REVISED
        proposal.save()
        
        messages.success(request, f"Revision {revision.revision_number} created.")
        return redirect('staff:proposal-detail', pk=proposal.pk)
    
    messages.error(request, "Error creating revision.")
    return redirect('staff:proposal-detail', pk=proposal.pk)


@login_required
@permission_required('profile.view_student', raise_exception=True)
@require_http_methods(["POST"])
def accept_proposal(request, pk):
    """Accept a proposal (student action)"""
    proposal = get_object_or_404(Proposal, pk=pk)
    
    if proposal.student != request.user:
        raise PermissionDenied
    
    proposal.status = Proposal.ACCEPTED
    proposal.accepted_at = timezone.now()
    proposal.save()
    
    # Create order from proposal
    order = Order.objects.create(
        student=proposal.student,
        date_paid=None,  # Not paid yet
    )
    
    # Create order line items from proposal line items
    for lineitem in proposal.proposallineitem_set.all():
        OrderLineItem.objects.create(
            order=order,
            product=lineitem.product,
            qty=lineitem.quantity,
            charge=lineitem.price,
            product_start_date=lineitem.start_date,
            product_end_date=lineitem.end_date,
        )
    
    # Update student balance
    proposal.student.update_account_balance()
    
    messages.success(request, "Proposal accepted. Order created.")
    return redirect('profile:view', pk=request.user.pk)


@login_required
@permission_required('profile.view_student', raise_exception=True)
@require_http_methods(["POST"])
def create_payment_plan(request, pk):
    """Create Stripe payment plan for proposal"""
    import stripe
    from django.conf import settings
    
    proposal = get_object_or_404(Proposal, pk=pk)
    
    if not proposal.has_payment_plan:
        messages.error(request, "This proposal doesn't have a payment plan configured.")
        return redirect('staff:proposal-detail', pk=proposal.pk)
    
    stripe.api_key = settings.STRIPE_SECRET_API_KEY
    
    try:
        # Create or get Stripe customer
        student = proposal.student
        if not student.stripe_customer_id:
            customer = stripe.Customer.create(
                email=student.email,
                name=f"{student.first_name} {student.last_name}",
                metadata={'student_id': student.pk}
            )
            student.stripe_customer_id = customer.id
            student.save(update_fields=['stripe_customer_id'])
        else:
            customer = stripe.Customer.retrieve(student.stripe_customer_id)
        
        # Calculate monthly payment
        monthly_amount = proposal.monthly_payment
        
        # Create Stripe product and price
        product = stripe.Product.create(
            name=f"Proposal {proposal.proposal_number} - Payment Plan",
            description=f"Payment plan for {proposal.title}",
        )
        
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(monthly_amount * 100),  # Convert to cents
            currency='usd',
            recurring={'interval': 'month'},
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': price.id}],
            metadata={'proposal_id': proposal.pk, 'student_id': student.pk},
        )
        
        # Create payment plan record
        payment_plan, created = ProposalPaymentPlan.objects.get_or_create(
            proposal=proposal,
            defaults={
                'total_amount': proposal.total_amount,
                'number_of_payments': proposal.payment_plan_months,
                'payment_frequency': 'monthly',
                'first_payment_date': proposal.payment_plan_start_date or timezone.now().date(),
                'regular_payment_amount': monthly_amount,
                'stripe_subscription_id': subscription.id,
                'stripe_price_id': price.id,
            }
        )
        
        if not created:
            payment_plan.stripe_subscription_id = subscription.id
            payment_plan.stripe_price_id = price.id
            payment_plan.save()
        
        # Update proposal
        proposal.stripe_subscription_id = subscription.id
        proposal.subscription_active = True
        proposal.save()
        
        # Update student
        student.stripe_subscription_id = subscription.id
        student.subscription_active = True
        student.save(update_fields=['stripe_subscription_id', 'subscription_active'])
        
        messages.success(request, "Payment plan created and subscription activated.")
        
    except Exception as e:
        messages.error(request, f"Error creating payment plan: {str(e)}")
    
    return redirect('staff:proposal-detail', pk=proposal.pk)
