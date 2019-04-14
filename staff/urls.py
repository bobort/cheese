from django.urls import path

from staff import views

app_name = 'staff'

urlpatterns = [
    path('', views.StudentListView.as_view(), name='staff-index'),
    path('students', views.StudentListView.as_view(), name='student-list'),
    path('zoom/create', views.ZoomIDCreateView.as_view(), name='zoom-create'),
    path('err', views.ThrowError.as_view(), name='throw-error'),
]
