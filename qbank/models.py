from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe

from tinymce.models import HTMLField


class Answer(models.Model):
    description = HTMLField()
    question = models.ForeignKey("qbank.Question", on_delete=models.DO_NOTHING)

    @mark_safe
    def __str__(self):
        return self.description[:100]


class Question(models.Model):
    description = HTMLField()
    correct_answer = models.ForeignKey(Answer, blank=True, null=True, on_delete=models.CASCADE, related_name="+")
    correct_answer_description = HTMLField()

    @mark_safe
    def __str__(self):
        return self.description[:100]


class UserQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    time_start = models.DateTimeField(auto_now_add=True)
    time_end = models.DateTimeField()
    chosen_answer = models.ForeignKey(Answer, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
