from django.db import models
from django.utils import timezone
from django.db.models import Sum,Avg
from decimal import Decimal


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)  # Код валюты (например, USD, EUR)

    def __str__(self):
        return self.code


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)  

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

        # Общий список валют
        currencies = Currency.objects.all()

        # Инициализируем данные для кассы
        self.total_cash = Decimal('100000.00')
        self.total_profit = Decimal('0.00')
        self.currency_data = []

        # Обработка каждой валюты
        for currency in currencies:
            currency_transactions = transactions.filter(currency=currency)

            # Рассчитываем общие покупки и продажи (количество валюты)
            total_bought = currency_transactions.filter(operation_type='buy').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')

            total_sold = currency_transactions.filter(operation_type='sell').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')

            # Средние курсы покупок и продаж
            avg_rate_bought = currency_transactions.filter(operation_type='buy').aggregate(
                avg_rate=Avg('rate')
            )['avg_rate'] or Decimal('0.00')

            avg_rate_sold = currency_transactions.filter(operation_type='sell').aggregate(
                avg_rate=Avg('rate')
            )['avg_rate'] or Decimal('0.00')

            # Профит по валюте
            profit = total_sold * (avg_rate_sold - avg_rate_bought)

            # Обновление общей кассы и общего профита
            self.total_cash -= total_bought * avg_rate_bought  # Уменьшение кассы при покупке
            self.total_cash += total_sold * avg_rate_sold      # Увеличение кассы при продаже
            self.total_profit += profit

            # Добавляем данные по текущей валюте
            self.currency_data.append({
                "currency": currency.code,
                "total_bought": total_bought,
                "avg_rate_bought": avg_rate_bought,
                "total_sold": total_sold,
                "avg_rate_sold": avg_rate_sold,
                "profit": profit
            })  

        # Сохраняем кассу
        self.save()

