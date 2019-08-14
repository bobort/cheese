import datetime

import dateutil
import pytz
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, UpdateView
from schedule.models import Calendar, Occurrence
from schedule.utils import check_calendar_permissions
from schedule.views import FullCalendarView

from profile.forms import OrderForm, StudentChangeForm
from profile.models import Order, Student


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


class CalendarView(FullCalendarView):
    template_name = "calendar.html"


@check_calendar_permissions
def api_occurrences(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    calendar_slug = request.GET.get("calendar_slug")
    timezone = request.GET.get("timezone")

    try:
        response_data = _api_occurrences(start, end, calendar_slug, timezone)
    except (ValueError, Calendar.DoesNotExist) as e:
        return HttpResponseBadRequest(e)

    return JsonResponse(response_data, safe=False)


def _api_occurrences(start, end, calendar_slug, timezone):
    if not start or not end:
        raise ValueError("Start and end parameters are required")
    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)
    current_tz = False
    if timezone and timezone in pytz.common_timezones:
        # make start and end dates aware in given timezone
        current_tz = pytz.timezone(timezone)
        start = current_tz.localize(start)
        end = current_tz.localize(end)

    if calendar_slug:
        # will raise DoesNotExist exception if no match
        calendars = [Calendar.objects.get(slug=calendar_slug)]
    # if no calendar slug is given, get all the calendars
    else:
        calendars = Calendar.objects.all()
    response_data = []
    # Algorithm to get an id for the occurrences in fullcalendar (NOT THE SAME
    # AS IN THE DB) which are always unique.
    # Fullcalendar thinks that all their "events" with the same "event.id" in
    # their system are the same object, because it's not really built around
    # the idea of events (generators)
    # and occurrences (their events).
    # Check the "persisted" boolean value that tells it whether to change the
    # event, using the "event_id" or the occurrence with the specified "id".
    # for more info https://github.com/llazzaro/django-scheduler/pull/169
    i = 1
    if Occurrence.objects.all().count() > 0:
        i = Occurrence.objects.latest("id").id + 1
    event_list = []
    for calendar in calendars:
        # create flat list of events from each calendar
        event_list += calendar.events.filter(start__lte=end).filter(
            Q(end_recurring_period__gte=start) | Q(end_recurring_period__isnull=True)
        )
    for event in event_list:
        occurrences = event.get_occurrences(start, end)
        for occurrence in occurrences:
            occurrence_id = i + occurrence.event.id
            existed = False
            if occurrence.id:
                occurrence_id = occurrence.id
                existed = True
            recur_rule = occurrence.event.rule.name if occurrence.event.rule else None
            if occurrence.event.end_recurring_period:
                recur_period_end = occurrence.event.end_recurring_period
                if current_tz:
                    # make recur_period_end aware in given timezone
                    recur_period_end = recur_period_end.astimezone(current_tz)
                recur_period_end = recur_period_end
            else:
                recur_period_end = None
            event_start = occurrence.start
            event_end = occurrence.end
            if current_tz:
                # make event start and end dates aware in given timezone
                event_start = event_start.astimezone(current_tz)
                event_end = event_end.astimezone(current_tz)

            response_data.append(
                {
                    "id": occurrence_id,
                    "title": occurrence.title,
                    "start": event_start,
                    "end": event_end,
                    "existed": existed,
                    "event_id": occurrence.event.id,
                    "color": occurrence.event.color_event,
                    "description": occurrence.description,
                    "rule": recur_rule,
                    "end_recurring_period": recur_period_end,
                    "creator": str(occurrence.event.creator),
                    "calendar": occurrence.event.calendar.slug,
                    "cancelled": occurrence.cancelled,
                }
            )
    return response_data
