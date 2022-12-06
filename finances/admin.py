from django.contrib import admin

from finances.models import BankTransaction, TransactionCategory, ApprovedTransaction


class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ['details', 'posting_date', 'description', 'amount', 'type']


admin.site.register(BankTransaction, BankTransactionAdmin)
admin.site.register(TransactionCategory)
admin.site.register(ApprovedTransaction)
