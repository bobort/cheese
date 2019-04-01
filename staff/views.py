from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView

from profile.models import Student, GroupSession
from staff.forms import GroupSessionAppointmentForm


class StudentListView(PermissionRequiredMixin, ListView):
    model = Student
    template_name = "student_list.html"
    permission_required = ['profile.view_student']

    def get_queryset(self):
        return super().get_queryset().filter(is_staff=False)


class ZoomIDCreateView(PermissionRequiredMixin, CreateView):
    model = GroupSession
    template_name = "zoom.html"
    permission_required = ["profile.create_groupsession"]
    form_class = GroupSessionAppointmentForm
    success_url = reverse_lazy("frontend:index")
