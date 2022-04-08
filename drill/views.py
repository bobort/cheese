from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView

from drill.forms import ConvertDrillForm
from drill.models import DrillTopic


class TopicDetail(UserPassesTestMixin, DetailView):
    model = DrillTopic

    def test_func(self):
        return self.request.user.can_access_drills


class TopicList(UserPassesTestMixin, ListView):
    model = DrillTopic

    def test_func(self):
        return self.request.user.can_access_drills


class ConvertDrill(CreateView):
    form_class = ConvertDrillForm
