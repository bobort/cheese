from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView, ListView

from drill.models import DrillTopic


class TopicDetail(PermissionRequiredMixin, DetailView):
    model = DrillTopic
    permission_required = ['drill.view_drilltopic']


class TopicList(PermissionRequiredMixin, ListView):
    model = DrillTopic
    permission_required = ['drill.view_drilltopic']
