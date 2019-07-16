from django.views.generic import TemplateView
from schedule.views import FullCalendarView


class IndexView(TemplateView):
    template_name = "index.html"


class ResourcesView(TemplateView):
    template_name = "resources.html"


class AboutView(TemplateView):
    template_name = "about.html"


class TestimonialsView(TemplateView):
    template_name = "section_testimonials.html"


class ServicesView(TemplateView):
    template_name = "services.html"


class ScheduleView(TemplateView):
    template_name = "schedule.html"


class PrivacyPolicyView(TemplateView):
    template_name = "legal/privacy_policy.html"


class TermsView(TemplateView):
    template_name = "legal/terms.html"


class DisclaimerView(TemplateView):
    template_name = "legal/disclaimer.html"


class ReturnPolicyView(TemplateView):
    template_name = "legal/return_policy.html"


class CalendarView(TemplateView):
    template_name = "calendar.html"
