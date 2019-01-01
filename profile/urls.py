from django.urls import path

from profile import views

app_name = 'profile'

urlpatterns = [
    path('pay', views.process_payment, name='pay'),
]
