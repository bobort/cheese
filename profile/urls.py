from django.urls import path

from profile import views, stripe_views

app_name = 'profile'

urlpatterns = [
    path('pay', views.process_payment, name='pay'),
    path('receipt/<int:pk>', views.Receipt.as_view(), name='receipt'),
    path('update/<int:pk>', views.ProfileUpdate.as_view(), name='update'),
    path('<int:pk>', views.ProfileView.as_view(), name='view'),
    # Stripe subscription endpoints
    path('stripe/create-subscription', stripe_views.create_subscription, name='create-subscription'),
    path('stripe/setup-payment', stripe_views.setup_payment_method, name='setup-payment'),
    path('stripe/cancel-subscription', stripe_views.cancel_subscription, name='cancel-subscription'),
    path('stripe/webhook', stripe_views.stripe_webhook, name='stripe-webhook'),
]
