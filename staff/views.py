from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import FieldError
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.views.generic.base import TemplateView

from profile.models import Student, Appointment


class StudentListView(PermissionRequiredMixin, ListView):
    model = Student
    template_name = "student_list.html"
    permission_required = ['profile.view_student']

    def get_queryset(self):
        order_by = self.request.GET.get('ordering')
        q = super().get_queryset().filter(is_staff=False)
        if order_by:
            try:
                return q.order_by(order_by)
            except FieldError:  # if ordering isn't an actual field
                return q
        return q


class AppointmentCreateView(PermissionRequiredMixin, CreateView):
    model = Appointment
    template_name = "appointment.html"
    permission_required = ["profile.create_appointment"]
    form_class = None


class ThrowError(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    def test_func(self):
        user = self.request.user
        return user.is_superuser

    def get_context_data(self, **kwargs):
        raise ValueError("Error purposefully generated.")
