from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "index.html"


class AboutView(TemplateView):
    template_name = "about.html"


class ServicesView(TemplateView):
    template_name = "services.html"


class ScheduleView(TemplateView):
    template_name = "schedule.html"
