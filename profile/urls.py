from django.urls import path

from profile.views import CreateRegistration, CreateProfile

app_name = 'profile'

urlpatterns = [
    path('register', CreateRegistration.as_view(), name="register"),
    path('create/<int:user>', CreateProfile.as_view(), name="create"),
]
