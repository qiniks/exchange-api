from django.urls import path
from .views import CashRegisterView, CurrencyListCreateView, UserListCreateView, TransactionListCreateView

urlpatterns = [
    path('currencies/', CurrencyListCreateView.as_view(), name='currency-list-create'),
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('cash-register/', CashRegisterView.as_view(), name='cash-register'),
]
