from rest_framework import serializers

from qbank.models import Question, Answer


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('vignette', 'correct_answer', 'explanation_summary')


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('description', 'question')