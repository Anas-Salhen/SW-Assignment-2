from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from .models import Income, Expense, Category, Budget
from django.db.models import Sum
from datetime import datetime


User = get_user_model()


class AuthManager ():
    def register(self,username, email, password):
        if not username or not password:
            raise ValueError("Missing fields")
        
        return User.objects.create_user(username, email, password)
            
    def login(self, request, username, password):
        if not username or not password:
            raise ValueError("Missing fields")
            
        user = self.validateCredentials(request, username, password)
        login(request, user)
        
    def validateCredentials(self,request, username, password):
        user = authenticate(request, username=username, password=password)
        if user is None:
            raise ValueError("Invalid credentials")
        return user
    

class TransactionManager:
    
    def calculateBalance(self, user):
        total_income = Income.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0
        return total_income - total_expense

    def add_income(self, user, amount, source, description=None):
        if float(amount) <= 0:
            raise ValueError("Amount must be positive")
        
        income = Income.objects.create(
            user=user, 
            amount=amount, 
            source=source, 
            description=description
        )
        return income, self.calculateBalance(user)

    def add_expense(self, user, amount, category_name, method, description=None):
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
            
        current_balance = self.calculateBalance(user)
        if amount > current_balance:
            raise ValueError("Insufficient balance!")

        category_obj, created = Category.objects.get_or_create(name=category_name)

        expense = Expense.objects.create(
            user=user, 
            amount=amount, 
            category=category_obj, 
            paymentMethod=method, 
            description=description
        )
        
        updated_balance = self.calculateBalance(user)
        
        return expense, updated_balance

    def filter_by_date(self, user, start_date, end_date):
        incomes = Income.objects.filter(
        user=user,
        date__range=(start_date, end_date)
    )
        expenses = Expense.objects.filter(
        user=user,
        date__range=(start_date, end_date)
    )
        return incomes, expenses

    def generate_pie_chart(self, expenses):
        return expenses.values('category__name').annotate(
            total=Sum('amount')
        )

    def generate_bar_chart(self, total_income, total_expense):
        return {
            "income": total_income,
            "expense": total_expense
        }

    def generate_report(self, user, month):
        # month format: "2026-01"
        start_date = datetime.strptime(month, "%Y-%m")

        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)

        incomes, expenses = self.filter_by_date(user, start_date, end_date)

        total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0

        pie_chart = self.generate_pie_chart(expenses)
        bar_chart = self.generate_bar_chart(total_income, total_expense)

        return {
            "status": "report_ready",
            "month": month,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_balance": total_income - total_expense,
            "pie_chart": list(pie_chart),
            "bar_chart": bar_chart
        }

class BudgetManager:
    def setBudget(user, amount, category_name, start, end):
        category_id = Category.objects.filter(name=category_name).id
        Budget.objects.update_or_create(user=user, category=category_id, amount=amount, start_date=start, end_date=end)

    def calculateRemaining(category_name, user):
        category_id = Category.objects.filter(name=category_name).id
        total_expense = Expense.objects.filter(user=user, category=category_id).aggregate(Sum('amount'))['amount__sum'] or 0
        limit = Budget.objects.filter(user=user, category=category_id).amount
        return limit - total_expense