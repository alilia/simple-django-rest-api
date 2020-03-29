from django.urls import path
from . import views

urlpatterns = [
	path('', views.DefaultView.as_view()),
	path('transactions/', views.TransactionView.as_view()), # POST, GET
	path('transactions/<transaction_id>/', views.TransactionView.as_view()), # GET, DELETE

	path('accounts/<account_id>/', views.AccountBreakdown.as_view()), # GET
	path('accounts/<account_id>/<date_from>/', views.AccountBreakdown.as_view()), # GET
	path('accounts/<account_id>/<date_from>/<date_to>/', views.AccountBreakdown.as_view()) # GET
]
