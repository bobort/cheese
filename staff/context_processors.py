from django.utils import timezone
from schedule.models import Event, Occurrence
from schedule.periods import Day


def get_event_occurrences_today(request):
    occurrences_to_save = Day(Event.objects.all(), timezone.now()).get_occurrences()
    for occurrence in occurrences_to_save:
        occurrence.save()
    return {'occurrences': Occurrence.objects.filter(pk__in=occurrences_to_save, roupsession__isnull=True), 'now': timezone.now()}
