from django.urls import path, include
from rest_framework import routers

from qbank import views

app_name = 'qbank'

router = routers.DefaultRouter()
router.register(r'questions', views.QuestionView, 'question')
router.register(r'answers', views.AnswerView, 'answer')

urlpatterns = [
    path('api/', include(router.urls))
]
