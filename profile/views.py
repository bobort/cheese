import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, UpdateView

from profile.forms import OrderForm, StudentChangeForm
from profile.models import Order, Student
# from profile.quickbooks import save_invoice
from utils import send_html_email, send_sms


@login_required
def process_payment(request):
    form = OrderForm(request.POST or None, user=request.user)
    if request.POST:
        # Set your secret key: remember to change this to your live secret key in production
        # See your keys here: https://dashboard.stripe.com/account/apikeys
        stripe.api_key = settings.STRIPE_SECRET_API_KEY

        # Get the payment token ID submitted by the form:
        token = request.POST.get('stripeToken')

        try:
            if token and form.is_valid():
                grand_total = form.grand_total
                if grand_total > 0:
                    stripe.Charge.create(
                        amount=int(grand_total * 100),  # stripe amounts are in pennies
                        currency='usd',
                        description='Ocean Ink',
                        source=token,
                        metadata={'student_id': request.user.pk},
                    )
                try:
                    # save_invoice(order)
                    pass
                except:
                    pass
                # send email message after everything is saved
                order = form.save()
                message = render_to_string('email_receipt.html', {'order': order})
                send_html_email(
                    "New Payment", message, ["matthew.pava@gmail.com", "drlepava@gmail.com"], order.student.email
                )
                send_html_email(
                    "Thank you for your payment.", message, [order.student.email], "matthew.pava@gmail.com"
                )
                products = ', '.join(order.orderlineitem_set.values_list('product__name', flat=True))
                send_sms.send(f"{order.student} bought ${order.grand_total}: {products}")
                return redirect(reverse('profile:receipt', kwargs={'pk': order.pk}))
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            form.card_errors = e.user_message
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            form.card_errors = "Server error: Stripe rate limit reached. Please try again."
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print("User: %s" % request.user)
            print("Invalid parameters sent to Stripe. %s" % e)
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            print("User: %s" % request.user)
            print("Invalid Stripe API key.")
        except stripe.error.APIConnectionError as e:
            print("User: %s" % request.user)
            print("Network communication with Stripe failed.")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            print("User: %s" % request.user)
            print("Generic Stripe error: %s" % e)

    return render(request, template_name="pay.html", context={
        'form': form, 'STRIPE_API_KEY': settings.STRIPE_PUBLISHABLE_API_KEY}
    )


class Receipt(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = "receipt.html"

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user == self.get_object().student


class ProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Student
    template_name = "view.html"

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user == self.get_object()


class ProfileUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Student
    form_class = StudentChangeForm
    template_name = "form.html"
    success_url = reverse_lazy('frontend:schedule')
    extra_context = {'title': "Update Profile"}

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user == self.get_object()
