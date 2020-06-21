from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView, ListView, CreateView

from drill.forms import ConvertDrillForm
from drill.models import DrillTopic


class TopicDetail(PermissionRequiredMixin, DetailView):
    model = DrillTopic
    permission_required = ['drill.view_drilltopic']


class TopicList(PermissionRequiredMixin, ListView):
    model = DrillTopic
    permission_required = ['drill.view_drilltopic']


class ConvertDrill(PermissionRequiredMixin, CreateView):
    form_class = ConvertDrillForm
    permission_required = []
