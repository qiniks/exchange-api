from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from django.db.models import Sum, F, Q, Avg
from decimal import Decimal


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)  # Код валюты (например, USD, EUR)

    def __str__(self):
        return self.code


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        if not username or not password:
            raise ValueError('The fields must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username


class Transaction(models.Model):
    OPERATION_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=4, choices=OPERATION_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    rate = models.DecimalField(max_digits=15, decimal_places=2)
    total = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.total = self.amount * self.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.operation_type.capitalize()} {self.amount} {self.currency.code} at {self.rate}"



class CashRegister(models.Model):
    total_cash = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('100000.00'))  # Стартовый остаток в сомах
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))  # Итоговый профит

    def update_register(self):
        transactions = Transaction.objects.all()

        # Рассчитать общий остаток с учетом покупок и продаж
        buy_total = transactions.filter(operation_type='buy').aggregate(total=Sum(F('amount') * F('rate')))['total'] or Decimal('0.00')
        sell_total = transactions.filter(operation_type='sell').aggregate(total=Sum(F('amount') * F('rate')))['total'] or Decimal('0.00')

        # Общий профит по продажам
        sell_profit = transactions.filter(operation_type='sell').aggregate(
            profit=Sum(F('amount') * F('rate')) - Sum(F('amount') * F('rate'), filter=Q(operation_type='buy'))
        )['profit'] or Decimal('0.00')

        # Обновление данных кассы
        self.total_cash = Decimal('100000.00') - buy_total + sell_total
        self.total_profit = sell_profit

        # Собираем информацию по каждой валюте
        self.currency_data = []
        currencies = Currency.objects.all()
        for currency in currencies:
            currency_transactions = transactions.filter(currency=currency)

            total_bought = currency_transactions.filter(operation_type='buy').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            avg_rate_bought = currency_transactions.filter(operation_type='buy').aggregate(avg_rate=Avg('rate'))['avg_rate'] or Decimal('0.00')

            total_sold = currency_transactions.filter(operation_type='sell').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            avg_rate_sold = currency_transactions.filter(operation_type='sell').aggregate(avg_rate=Avg('rate'))['avg_rate'] or Decimal('0.00')

            profit = currency_transactions.filter(operation_type='sell').aggregate(
                profit=Sum(F('amount') * F('rate')) - Sum(F('amount') * F('rate'), filter=Q(operation_type='buy'))
            )['profit'] or Decimal('0.00')

            self.currency_data.append({
                "currency": currency.code,
                "total_bought": total_bought,
                "avg_rate_bought": avg_rate_bought,
                "total_sold": total_sold,
                "avg_rate_sold": avg_rate_sold,
                "profit": profit
            })

        self.save()
