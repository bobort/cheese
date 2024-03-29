from django.urls import path

from drill import views

app_name = "drill"

urlpatterns = [
    path('', views.TopicList.as_view(), name="topics"),
    path('<int:pk>', views.TopicDetail.as_view(), name="questions"),
    path('track/<int:pk>', views.TrackDrill.as_view(), name="drill-track"),
]
