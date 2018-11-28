from django.urls import path

from frontend import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('about/?', views.AboutView.as_view(), name='about'),
    path('services/?', views.ServicesView.as_view(), name='services'),
    path('pricing?', views.PricingView.as_view(), name='pricing'),
]
