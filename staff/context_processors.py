from django.utils import timezone
from schedule.models import Event
from schedule.periods import Day


def get_event_occurrences_today(request):
    occurrences_to_save = Day(Event.objects.all(), timezone.now()).get_occurrences()
    for occurrence in occurrences_to_save:
        occurrence.save()
    return {'occurrences': occurrences_to_save, 'now': timezone.now()}
