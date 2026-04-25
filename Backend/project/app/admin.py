from django.contrib import admin
from .models import Income, Expense, Category

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'source', 'date') # عشان يظهر المبلغ والمصدر

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'date') # عشان يظهر المبلغ والفئة

admin.site.register(Category)