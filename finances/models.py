from django.db import models


class BankTransaction(models.Model):
    details = models.TextField()
    posting_date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    type = models.TextField()


class TransactionCategory(models.Model):
    name = models.TextField()


class ApprovedTransaction(models.Model):
    transaction_id = models.ForeignKey(BankTransaction, on_delete=models.CASCADE)
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE)
    approval_date = models.DateField(auto_now=True)
    notes = models.TextField()
    contact = models.ForeignKey("profile.Student", on_delete=models.CASCADE, blank=True, null=True)
    document = models.FileField(upload_to="bank/", blank=True, null=True)
    contact_order = models.ForeignKey("profile.Order", on_delete=models.DO_NOTHING, blank=True, null=True)
