from rest_framework import viewsets

from qbank.models import Question, Answer
from qbank.serializers import QuestionSerializer, AnswerSerializer


class QuestionView(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


class AnswerView(viewsets.ModelViewSet):
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()
