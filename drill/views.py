from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView

from drill.forms import ConvertDrillForm
from drill.models import DrillTopic


class TopicDetail(UserPassesTestMixin, DetailView):
    model = DrillTopic

    def test_func(self):
        return self.request.user.productuser_set.filter(
            product_end_date__gte=timezone.now().date(),
            product__name="Ocean Courage Group Sessions"
        ).exists()


class TopicList(UserPassesTestMixin, ListView):
    model = DrillTopic

    def test_func(self):
        return self.request.user.productuser_set.filter(
            product_end_date__gte=timezone.now().date(),
            product__name="Ocean Courage Group Sessions"
        ).exists()


class ConvertDrill(CreateView):
    form_class = ConvertDrillForm
