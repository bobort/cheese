"""
Stripe subscription payment views for account balance payments
"""
import stripe
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from profile.models import Student, StripePayment

stripe.api_key = settings.STRIPE_SECRET_API_KEY


@login_required
def create_subscription(request):
    """Create a Stripe subscription for paying account balance"""
    student = request.user
    
    if student.account_balance <= 0:
        messages.error(request, "You don't have an outstanding balance.")
        return redirect('profile:view', pk=student.pk)
    
    try:
        # Create or retrieve Stripe customer
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
        
        # Create subscription for balance payment
        # Use a price that matches the balance amount
        # For subscriptions, we'll create a recurring payment plan
        # Since balance changes, we'll use a fixed amount subscription that can be updated
        
        # Create a price for the subscription (monthly payment)
        # Calculate monthly payment amount (balance / number of months, or minimum $10)
        # Ensure we have a valid balance
        if student.account_balance <= 0:
            return JsonResponse({'error': 'No outstanding balance'}, status=400)
        
        monthly_amount = max(Decimal('10.00'), student.account_balance / Decimal('12'))
        
        # Create a product and price for this subscription
        product = stripe.Product.create(
            name=f"Account Balance Payment - {student.get_full_name()}",
            metadata={'student_id': student.pk}
        )
        
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(monthly_amount * 100),  # Convert to cents
            currency='usd',
            recurring={'interval': 'month'},
            metadata={'student_id': student.pk}
        )
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{'price': price.id}],
            metadata={
                'student_id': student.pk,
                'account_balance': str(student.account_balance),
                'type': 'balance_payment'
            },
            collection_method='charge_automatically',
            payment_behavior='default_incomplete',
            payment_settings={'save_default_payment_method': 'on_subscription'},
            expand=['latest_invoice.payment_intent'],
        )
        
        student.stripe_subscription_id = subscription.id
        student.subscription_active = True
        student.save(update_fields=['stripe_subscription_id', 'subscription_active'])
        
        return JsonResponse({
            'subscriptionId': subscription.id,
            'clientSecret': subscription.latest_invoice.payment_intent.client_secret,
        })
        
    except stripe.error.StripeError as e:
        messages.error(request, f"Error creating subscription: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def setup_payment_method(request):
    """Setup payment method for subscription"""
    student = request.user
    
    if not student.stripe_customer_id:
        messages.error(request, "Please create a subscription first.")
        return redirect('profile:view', pk=student.pk)
    
    try:
        intent = stripe.SetupIntent.create(
            customer=student.stripe_customer_id,
            payment_method_types=['card'],
            metadata={'student_id': student.pk}
        )
        
        return JsonResponse({
            'clientSecret': intent.client_secret
        })
    except stripe.error.StripeError as e:
        messages.error(request, f"Error setting up payment: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def cancel_subscription(request):
    """Cancel the active subscription"""
    student = request.user
    
    if not student.stripe_subscription_id:
        messages.error(request, "No active subscription found.")
        return redirect('profile:view', pk=student.pk)
    
    try:
        subscription = stripe.Subscription.retrieve(student.stripe_subscription_id)
        subscription.cancel_at_period_end = True
        subscription.save()
        
        messages.success(request, "Subscription will be canceled at the end of the billing period.")
    except stripe.error.StripeError as e:
        messages.error(request, f"Error canceling subscription: {str(e)}")
    
    return redirect('profile:view', pk=student.pk)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_payment_succeeded(invoice)
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    
    return JsonResponse({'status': 'success'})


def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    subscription_id = invoice.get('subscription')
    if not subscription_id:
        return
    
    try:
        student = Student.objects.get(stripe_subscription_id=subscription_id)
        amount = Decimal(invoice['amount_paid']) / Decimal('100')
        
        # Create payment record
        StripePayment.objects.create(
            student=student,
            stripe_payment_intent_id=invoice.get('payment_intent', ''),
            stripe_invoice_id=invoice['id'],
            amount=amount,
            status='succeeded',
            paid_at=timezone.now(),
            metadata={'invoice': invoice}
        )
        
        # Update student balance
        student.account_balance = max(Decimal('0.00'), student.account_balance - amount)
        if student.account_balance <= 0:
            student.balance_paid = True
            # Cancel subscription if balance is paid
            if student.stripe_subscription_id:
                try:
                    subscription = stripe.Subscription.retrieve(student.stripe_subscription_id)
                    subscription.cancel()
                    student.subscription_active = False
                except:
                    pass
        
        student.save(update_fields=['account_balance', 'balance_paid', 'subscription_active'])
        
    except Student.DoesNotExist:
        pass


def handle_payment_failed(invoice):
    """Handle failed payment"""
    subscription_id = invoice.get('subscription')
    if not subscription_id:
        return
    
    try:
        student = Student.objects.get(stripe_subscription_id=subscription_id)
        amount = Decimal(invoice['amount_due']) / Decimal('100')
        
        # Create payment record
        StripePayment.objects.create(
            student=student,
            stripe_payment_intent_id=invoice.get('payment_intent', ''),
            stripe_invoice_id=invoice['id'],
            amount=amount,
            status='failed',
            metadata={'invoice': invoice}
        )
        
    except Student.DoesNotExist:
        pass


def handle_subscription_deleted(subscription):
    """Handle subscription deletion"""
    try:
        student = Student.objects.get(stripe_subscription_id=subscription['id'])
        student.subscription_active = False
        student.save(update_fields=['subscription_active'])
    except Student.DoesNotExist:
        pass


def handle_subscription_updated(subscription):
    """Handle subscription updates"""
    try:
        student = Student.objects.get(stripe_subscription_id=subscription['id'])
        # Update subscription status
        student.subscription_active = subscription['status'] in ['active', 'trialing']
        student.save(update_fields=['subscription_active'])
    except Student.DoesNotExist:
        pass

