from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import FieldError
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from profile.models import Student, GroupSession, Appointment
from staff.forms import GroupSessionAppointmentForm


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


class ZoomIDCreateView(PermissionRequiredMixin, CreateView):
    model = GroupSession
    template_name = "zoom.html"
    permission_required = ["profile.create_groupsession"]
    form_class = GroupSessionAppointmentForm
    success_url = reverse_lazy("frontend:index")


class AppointmentCreateView(PermissionRequiredMixin, CreateView):
    model = Appointment
    template_name = "appointment.html"
    permission_required = ["profile.create_appointment"]
    form_class = None