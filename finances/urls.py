from django.urls import path

from finances import views

app_name = 'finances'

urlpatterns = [
    path('upload', views.UploadBankTransactionView.as_view(), name='upload'),
    path('list', views.BankTransactionView.as_view(), name='list'),
]
