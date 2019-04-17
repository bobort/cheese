import datetime
from django.utils import timezone
from schedule.models import Event, Occurrence
from schedule.periods import Day

from profile.models import GroupSession

GROUPSESSION_TITLES = ["Morning Cute", "Drill Session"]


def get_event_occurrences_today(request):
    today = timezone.now()
    occurrences_to_save = Day(Event.objects.all(), today).get_occurrences()
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
