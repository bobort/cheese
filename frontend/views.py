from django.views.generic import TemplateView, ListView

from profile.models import Testimonial


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(*args, **kwargs)
        context['testimonial_list'] = Testimonial.objects.all()
        return context

class ResourcesView(TemplateView):
    template_name = "resources.html"


class AboutView(TemplateView):
    template_name = "about.html"


class TestimonialsView(ListView):
    template_name = "section_testimonials.html"
    model = Testimonial


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
