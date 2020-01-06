import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, UpdateView

from profile.forms import OrderForm, StudentChangeForm
from profile.models import Order, Student
# from profile.quickbooks import save_invoice


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
                order = form.save()
                charge = stripe.Charge.create(
                    amount=int(order.grand_total * 100),  # stripe amounts are in pennies
                    currency='usd',
                    description='Ocean Ink',
                    source=token,
                    metadata={'student_id': request.user.pk},
                )
                if charge.paid:
                    try:
                        # save_invoice(order)
                        pass
                    except:
                        pass
                    return redirect(reverse('profile:receipt', kwargs={'pk': order.pk}))
                else:
                    print("User: %s" % request.user)
                    print("Stripe charge not paid. %s" % charge)
                    return render(request, status=500)
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            print("User: %s" % request.user)
            print("Status is: %s" % e.http_status)
            print("Type is: %s" % err.get('type'))
            print("Code is: %s" % err.get('code'))
            # param is '' in this case
            print("Param is: %s" % err.get('param'))
            print("Message is: %s" % err.get('message'))
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            print("User: %s" % request.user)
            print("Stripe rate limit reached.")
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
