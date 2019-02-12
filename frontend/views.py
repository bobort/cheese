from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "index.html"


class AboutView(TemplateView):
    template_name = "about.html"


class TestimonialsView(TemplateView):
    template_name = "testimonials.html"


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
