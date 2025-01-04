from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CashRegister, Currency, User, Transaction
from .serializers import CashRegisterSerializer, CurrencySerializer, UserRegistrationSerializer, UserSerializer, TransactionSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password

class CurrencyListCreateView(generics.ListCreateAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Currency created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserAuthenticationView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Простая проверка имени пользователя и пароля
        try:
            user = User.objects.get(username=username, password=password)
            return Response(
                {"message": "Authentication successful.", "user_id": user.id},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )



class TransactionListCreateView(APIView):
    def get(self, request):
        transactions = Transaction.objects.all().order_by('-date')
        serializer = TransactionSerializer(transactions, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Transaction created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class TransactionUpdateView(APIView):
    def put(self, request, pk):
        """Обновление всей транзакции"""
        transaction = get_object_or_404(Transaction, pk=pk)
        serializer = TransactionSerializer(transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Частичное обновление транзакции"""
        transaction = get_object_or_404(Transaction, pk=pk)
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CashRegisterView(APIView):
    def get(self, request):
        # Получаем единственную запись кассы
        register, created = CashRegister.objects.get_or_create(id=1)

        # Обновляем данные кассы перед отправкой
        register.update_register()

        serializer = CashRegisterSerializer(register)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClearDatabaseView(APIView):
    """
    Очищает таблицы Transaction и CashRegister.
    """
    def post(self, request):
        Transaction.objects.all().delete()
        CashRegister.objects.all().delete()
        return Response({"message": "Таблицы очищены."}, status=status.HTTP_200_OK)


class DeleteUserView(APIView):
    """
    Удаление пользователя по ID.
    """
    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response({"message": f"Пользователь с ID {user_id} удален."}, status=status.HTTP_200_OK)


class DeleteCurrencyView(APIView):
    """
    Удаление валюты по ID.
    """
    def delete(self, request, currency_id):
        currency = get_object_or_404(Currency, id=currency_id)
        currency.delete()
        return Response({"message": f"Валюта с ID {currency_id} удалена."}, status=status.HTTP_200_OK)


class DeleteTransactionView(APIView):
    """
    Удаление транзакции по ID.
    """
    def delete(self, request, transaction_id):
        transaction = get_object_or_404(Transaction, id=transaction_id)
        transaction.delete()
        return Response({"message": f"Транзакция с ID {transaction_id} удалена."}, status=status.HTTP_200_OK)