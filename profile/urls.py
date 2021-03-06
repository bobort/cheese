from django.urls import path

from profile import views

app_name = 'profile'

urlpatterns = [
    path('pay', views.process_payment, name='pay'),
    path('receipt/<int:pk>', views.Receipt.as_view(), name='receipt'),
    path('update/<int:pk>', views.ProfileUpdate.as_view(), name='update'),
    path('<int:pk>', views.ProfileView.as_view(), name='view'),
]
