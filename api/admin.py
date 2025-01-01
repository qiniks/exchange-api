from django.contrib import admin
from .models import CashRegister, Currency, User, Transaction

# Register your models here.
admin.site.register(Currency)
admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(CashRegister)