from django.urls import path

from staff import views

app_name = 'staff'

urlpatterns = [
    path('', views.StudentListView.as_view(), name='staff-index'),
    path('students', views.StudentListView.as_view(), name='staff-student-list'),
]
