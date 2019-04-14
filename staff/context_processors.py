from datetime import timedelta
from django.utils import timezone
from schedule.models import Event, Occurrence
from schedule.periods import Day, Period

from profile.models import GroupSession


def get_event_occurrences_today(request):
    occurrences_to_save = Day(Event.objects.all(), timezone.now()).get_occurrences()
    # set the Zoom ID for the Morning Cute event to be the same as the previous one
    for occurrence in occurrences_to_save:
        occurrence.save()
        if not GroupSession.objects.filter(occurrence=occurrence).exists() and occurrence.event.title == "Morning Cute":
            event_occurrences = occurrence.event.get_occurrences(timezone.now() - timedelta(days=7), timezone.now())
            groupsession_occurrences = Occurrence.objects.filter(
                pk__in=[o.pk for o in event_occurrences], groupsession__isnull=False
            )
            last_occurrence = groupsession_occurrences.order_by('-start').first()
            if last_occurrence:
                GroupSession.objects.create(occurrence=occurrence, zoom_id=last_occurrence.groupsession.zoom_id)
    return {
        'occurrences': occurrences_to_save,
        'now': timezone.now()
    }
