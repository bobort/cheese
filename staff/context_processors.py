import datetime

from django.template.defaultfilters import date
from django.utils import timezone
from django.utils.translation import ugettext
from django.conf import settings as django_settings
from schedule.models import Event, Occurrence
from schedule.periods import Day, Period

from profile.models import GroupSession

GROUPSESSION_TITLES = ["Morning Cute", "Drill Session"]


def new_occurrence_hash(self):
    # monkey patch for Unhashable Type Occurrence
    return hash((self.original_start, self.original_end))


Occurrence.__hash__ = new_occurrence_hash


# todo we are using the template filter to show a utc date as the local server time
# todo   but that wasn't working properly, so we used timezone.localtime
def new_occurrence_str(self):
    return ugettext("%(start)s to %(end)s") % {
        'start': date(timezone.localtime(self.start), django_settings.DATETIME_FORMAT),
        'end': date(timezone.localtime(self.end), django_settings.DATETIME_FORMAT)
    }


Occurrence.__str__ = new_occurrence_str


def get_event_occurrences_today(request):
    today = timezone.localtime(timezone.now())  # Go to local server time for appointment modifications
    start = today - datetime.timedelta(days=7)
    end = today + datetime.timedelta(days=7)
    # todo: does get_occurrences return a pk for occurrences already in the database?
    occurrences_to_save = Period(Event.objects.all(), start, end).get_occurrences()
    # set the Zoom ID for the group session events to be the same as the previous one
    for occurrence in occurrences_to_save:
        occurrence.save()
        if not GroupSession.objects.filter(occurrence=occurrence).exists()\
                and occurrence.event.title in GROUPSESSION_TITLES:
            # look 7 days into the past to try to find an occurrence of the event
            event_occurrences = occurrence.event.get_occurrences(today - datetime.timedelta(days=7), today)
            groupsession_occurrences = Occurrence.objects.filter(
                pk__in=[o.pk for o in event_occurrences], groupsession__isnull=False
            )
            last_occurrence = groupsession_occurrences.order_by('-start').first()
            if last_occurrence:
                GroupSession.objects.create(occurrence=occurrence, zoom_id=last_occurrence.groupsession.zoom_id)
    return {
        'occurrences': occurrences_to_save,
        'now': today
    }
