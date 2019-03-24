from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from profile.models import Student


class StudentListView(PermissionRequiredMixin, ListView):
    model = Student
    template = "student_list.html"
    permission_required = ['profile.view_student']

    def get_queryset(self):
        return super().get_queryset().filter(is_staff=False)

