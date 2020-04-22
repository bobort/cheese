from django.views.generic import DetailView, ListView

from drill.models import DrillTopic


class TopicDetail(DetailView):
    model = DrillTopic


class TopicList(ListView):
    model = DrillTopic
