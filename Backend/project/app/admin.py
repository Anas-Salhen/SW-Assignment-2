from django.contrib import admin
from .models import Income, Expense, Category

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'source', 'date') 

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
     list_display = ('user', 'title', 'amount', 'paymentMethod', 'date')
admin.site.register(Category)