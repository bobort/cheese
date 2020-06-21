from django.db import models
from django.urls import reverse
from tinymce.models import HTMLField


class DrillTopic(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse('drill:questions', kwargs={'pk': self.pk})


def get_last_drill_topic():
    return DrillTopic.objects.last().id


class Question(models.Model):
    topic = models.ForeignKey(DrillTopic, on_delete=models.CASCADE, default=get_last_drill_topic)
    q = HTMLField()
    a = HTMLField()

    class Meta:
        ordering = ('id', )

    def __str__(self):
        return f"{self.q[:100]}"
