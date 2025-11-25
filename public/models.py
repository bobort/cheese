from django.db import models


# Create your models here.
class Testimonial(models.Model):
    testimonial = models.TextField()
    citation = models.CharField(max_length=255)

    class Meta:
        ordering = ("-pk",)


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    slug = models.SlugField()

    def __str__(self):
        return self.question
