from django.urls import path

from frontend import views

app_name = 'frontend'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about', views.AboutView.as_view(), name='about'),
    path('services', views.ServicesView.as_view(), name='services'),
    path('schedule', views.ScheduleView.as_view(), name='schedule'),
    path('legal/privacy-policy', views.PrivacyPolicyView.as_view(), name='privacy-policy'),
    path('legal/terms', views.TermsView.as_view(), name='terms'),
    path('legal/disclaimer', views.DisclaimerView.as_view(), name='disclaimer'),
    path('legal/return-policy', views.ReturnPolicyView.as_view(), name='return-policy'),
]
