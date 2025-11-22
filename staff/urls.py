from django.urls import path

from staff import views

app_name = 'staff'

urlpatterns = [
    path('', views.IndexView.as_view(), name='staff-index'),
    path('dashboard', views.StaffDashboardView.as_view(), name='dashboard'),
    path('students', views.StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>', views.StudentDetailView.as_view(), name='student-detail'),
    path('orders', views.OrderLineItemListView.as_view(), name='orderlineitem-list'),
    path('ocean-courage', views.OceanCourageSubscribersView.as_view(), name='ocean-courage-list'),
    path('err', views.ThrowError.as_view(), name='throw-error'),
    path('contract', views.SignTerms.as_view(), name='contract'),
    # HTMX endpoints
    path('api/student/<int:pk>/balance', views.student_balance_partial, name='student-balance-partial'),
    # Proposal URLs
    path('proposals', views.ProposalListView.as_view(), name='proposal-list'),
    path('proposals/create', views.ProposalCreateView.as_view(), name='proposal-create'),
    path('proposals/<int:pk>', views.ProposalDetailView.as_view(), name='proposal-detail'),
    path('proposals/<int:pk>/edit', views.ProposalUpdateView.as_view(), name='proposal-update'),
    path('proposals/<int:pk>/send-email', views.send_proposal_email, name='proposal-send-email'),
    path('proposals/<int:pk>/add-comment', views.add_proposal_comment, name='proposal-add-comment'),
    path('proposals/<int:pk>/create-revision', views.create_proposal_revision, name='proposal-create-revision'),
    path('proposals/<int:pk>/accept', views.accept_proposal, name='proposal-accept'),
    path('proposals/<int:pk>/create-payment-plan', views.create_payment_plan, name='proposal-create-payment-plan'),
]
