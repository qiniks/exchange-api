from rest_framework import serializers
from .models import Currency, User, Transaction, CashRegister

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password','date_created']


class TransactionSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False) 

    currency = serializers.SlugRelatedField(
        queryset=Currency.objects.all(),
        slug_field='code'  # Указываем, что вместо id будет использоваться code
    )

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'currency', 'operation_type', 'amount', 'rate', 'total', 'date']



class CashRegisterSerializer(serializers.ModelSerializer):
    currency_data = serializers.SerializerMethodField()

    class Meta:
        model = CashRegister
        fields = ['total_cash', 'total_profit', 'currency_data']

    def get_currency_data(self, obj):
        return obj.currency_data
