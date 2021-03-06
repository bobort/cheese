from django.db import models

from tinymce.models import HTMLField

from profile.models import Student


class IndependentContractorTerms(models.Model):
    document = HTMLField()
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ('-date', )

    def __str__(self):
        return f"{self.date} - {self.document.replace('<p>', '')[:20]}..."


class ElectronicSignature(models.Model):
    staff_member = models.ForeignKey(Student, on_delete=models.CASCADE)
    initials = models.CharField(max_length=5)
    date = models.DateField()
    document = models.ForeignKey(IndependentContractorTerms, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-date', )

    def __str__(self):
        return f"{self.initials} - {self.date} - {self.staff_member}"
