from dateutil.parser import parse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from finances.forms import UploadBankTransaction, get_csv
from finances.models import BankTransaction


class UploadBankTransactionView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = UploadBankTransaction
    template_name = "upload.html"
    success_url = reverse_lazy("finances:list")

    def form_valid(self, form):
        csv = get_csv(form.cleaned_data['file'])
        transactions = []
        next(csv)  # dispose of header
        for row in csv:
            if row:
                transactions.append(BankTransaction(
                    details=row[0],
                    posting_date=parse(row[1]),
                    description=row[2],
                    amount=row[3],
                    type=row[4]
                ))
                # don't take too much memory
                if len(transactions) > 5000:
                    BankTransaction.objects.bulk_create(transactions)
                    transactions = []
        BankTransaction.objects.bulk_create(transactions)
        return super(UploadBankTransactionView, self).form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser


class BankTransactionView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = BankTransaction
    paginate_by = 100

    def test_func(self):
        return self.request.user.is_superuser
