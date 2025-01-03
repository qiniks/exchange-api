from django.urls import path
from .views import CashRegisterView, ClearDatabaseView, CurrencyListCreateView, DeleteCurrencyView, DeleteTransactionView, DeleteUserView, TransactionUpdateView, UserListCreateView, TransactionListCreateView

urlpatterns = [
    path('currencies/', CurrencyListCreateView.as_view(), name='currency-list-create'),
    path('currencies/delete/<int:currency_id>/', DeleteCurrencyView.as_view(), name='delete-currency'),

    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/delete/<int:user_id>/', DeleteUserView.as_view(), name='delete-user'),

    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('transactions/<int:pk>/', TransactionUpdateView.as_view(), name='transaction-update'),
    path('transactions/delete/<int:transaction_id>/', DeleteTransactionView.as_view(), name='delete-transaction'),

    path('cash-register/', CashRegisterView.as_view(), name='cash-register'),
    path('clear-database/', ClearDatabaseView.as_view(), name='clear-database'),
]
