from django.urls import path

from staff import views

app_name = 'staff'

urlpatterns = [
    path('', views.IndexView.as_view(), name='staff-index'),
    path('students', views.StudentListView.as_view(), name='student-list'),
    path('orders', views.OrderLineItemListView.as_view(), name='orderlineitem-list'),
    path('ocean-courage', views.OceanCourageSubscribersView.as_view(), name='ocean-courage-list'),
    path('err', views.ThrowError.as_view(), name='throw-error'),
]
