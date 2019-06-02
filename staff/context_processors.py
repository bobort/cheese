import datetime

from django.template.defaultfilters import date
from django.utils import timezone
from django.utils.translation import ugettext
from django.conf import settings as django_settings
from schedule.models import Event, Occurrence
from schedule.periods import Period


def new_occurrence_hash(self):
    # monkey patch for Unhashable Type Occurrence
    return hash((self.original_start, self.original_end))


Occurrence.__hash__ = new_occurrence_hash


# todo we are using the template filter to show a utc date as the local server time
# todo   but that wasn't working properly, so we are now using timezone.localtime
def new_occurrence_str(self):
    return ugettext("%(start)s to %(end)s") % {
        'start': date(timezone.localtime(self.start), django_settings.DATETIME_FORMAT),
        'end': date(timezone.localtime(self.end), django_settings.DATETIME_FORMAT)
    }


Occurrence.__str__ = new_occurrence_str


def get_event_occurrences_today(request):
    now = timezone.now()
    start = now
    end = now + datetime.timedelta(hours=1)
    occurrences = Period(Event.objects.all(), start, end).get_occurrences()
    # set the Zoom ID for the group session events to be the same as the previous one
    return {
        'occurrences': occurrences,
        'now': now,
    }
