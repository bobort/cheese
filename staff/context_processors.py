from django.utils import timezone
from schedule.models import Event, Occurrence
from schedule.periods import Day


def get_event_occurrences_today(request):
    occurrences_to_save = Day(Event.objects.all(), timezone.now()).get_occurrences()
    occurrences_to_save = Occurrence.objects.filter(
        pk__in=[o.pk for o in occurrences_to_save],
        groupsession__isnull=True
    )
    for occurrence in occurrences_to_save:
        occurrence.save()
    return {
        'occurrences': occurrences_to_save,
        'now': timezone.now()
    }
