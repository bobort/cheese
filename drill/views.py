from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import JsonResponse, Http404, HttpResponseNotFound
from django.views.generic import DetailView, ListView, CreateView

from drill.forms import ConvertDrillForm
from drill.models import DrillTopic, DrillTracking, Question


class TopicDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = DrillTopic

    def test_func(self):
        if self.request.user:
            return self.request.user.can_access_drills
        return self.request.user.is_superuser


class TopicList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = DrillTopic

    def test_func(self):
        if self.request.user:
            return self.request.user.can_access_drills
        return self.request.user.is_superuser


class ConvertDrill(CreateView):
    form_class = ConvertDrillForm


class TrackDrill(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    def test_func(self):
        if self.request.user:
            return self.request.user.can_access_drills
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound("GET not allowed.")

    def post(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            try:
                DrillTracking.objects.create(
                    student=request.user,
                    question=Question.objects.get(pk=self.kwargs.get('pk', -1))
                )
            except Question.DoesNotExist:
                return HttpResponseNotFound("Invalid question ID.")
            return JsonResponse({})
        return HttpResponseNotFound("Request must be XMLHttpRequest.")
