from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import FieldError, PermissionDenied
from django.db.models import Case, When, Max, F, Q
from django.urls import reverse
from django.views.generic import ListView, CreateView
from django.views.generic.base import TemplateView, RedirectView

from profile.models import Student, Appointment
from utils import divide_chunks


class IndexView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.groups.filter(name="oceancouragegroup").exists():
            return reverse("staff:ocean-courage-list")
        elif self.request.user.groups.filter(name="instructorgroup").exists() or self.request.user.is_superuser:
            return reverse("staff:student-list")
        raise PermissionDenied


class StudentListView(PermissionRequiredMixin, ListView):
    model = Student
    template_name = "staff/student_list.html"
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

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['marketing_list_chunks'] = divide_chunks(self.get_queryset().filter(marketing_subscription=True), 90)
        return context


class AppointmentCreateView(PermissionRequiredMixin, CreateView):
    model = Appointment
    template_name = "appointment.html"
    permission_required = ["profile.create_appointment"]
    form_class = None


class OceanCourageSubscribersView(PermissionRequiredMixin, ListView):
    model = Student
    template_name = "staff/oceancourage_list.html"

    def has_permission(self):
        # you must have a staff account and the student must be a subscriber
        # to the Ocean Courage package
        return self.request.user.groups.filter(name="oceancouragegroup").exists() or self.request.user.is_superuser

    def get_queryset(self):
        order_by = self.request.GET.get('ordering')
        q = super().get_queryset().filter(
            Q(order__orderlineitem__product__name="Ocean Courage Group Sessions") |
            Q(order__orderlineitem__product__name="USMLE STEP2CK/3 & COMLEX LEVEL 2/3 Course")
        ).annotate(
            last_purchase_date=Max('order__date_paid')
        )

        if order_by:
            try:
                return q.order_by(order_by)
            except FieldError:  # if ordering isn't an actual field
                return q
        return q


class ThrowError(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    def test_func(self):
        user = self.request.user
        return user.is_superuser

    def get_context_data(self, **kwargs):
        raise ValueError("Error purposefully generated.")
