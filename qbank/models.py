from django.db import models

from tinymce.models import HTMLField


class Answer(models.Model):
    description = HTMLField()


class Question(models.Model):
    description = HTMLField()
    correct_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    answers = models.ManyToManyField(Answer)
    correct_answer_reason = HTMLField()
