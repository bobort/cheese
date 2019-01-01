import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from profile.forms import PaymentForm


@login_required
def process_payment(request):
    form = PaymentForm(request.POST or None, user=request.user)
    if request.POST:
        # Set your secret key: remember to change this to your live secret key in production
        # See your keys here: https://dashboard.stripe.com/account/apikeys
        stripe.api_key = settings.STRIPE_API_KEY

        # Get the payment token ID submitted by the form:
        token = request.POST.get('stripeToken')

        try:
            if token and form.is_valid():
                charge = stripe.Charge.create(
                    amount=form.total,
                    currency='usd',
                    description='Ocean Ink',
                    source=token,
                )
                if charge.paid:
                    form.save()
                    return redirect(reverse('frontend:schedule'))
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

    return render(request, template_name="pay.html", context={'form': form, 'STRIPE_API_KEY': settings.STRIPE_API_KEY})
