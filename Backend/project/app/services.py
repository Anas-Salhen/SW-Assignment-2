from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from .models import Income, Expense, Category, Budget, Transaction
from django.db.models import Sum
from datetime import datetime


User = get_user_model()


class AuthManager():
    def register(self, username, email, password):
        if not username or not password:
            raise ValueError("Missing fields")
        return User.objects.create_user(username, email, password)

    def login(self, request, username, password):
        if not username or not password:
            raise ValueError("Missing fields")
        user = self.validateCredentials(request, username, password)
        login(request, user)

    def validateCredentials(self, request, username, password):
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
            title=description or source,
            transaction_type='income'
        )
        return income, self.calculateBalance(user)

    def add_expense(self, user, amount, category_name, method, description=None):
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")

        current_balance = self.calculateBalance(user)
        if amount > current_balance:
            raise ValueError("Insufficient balance!")

        expense = Expense.objects.create(
            user=user,
            amount=amount,
            paymentMethod=method,
            title=description or category_name,
            transaction_type='expense'
        )
        return expense, self.calculateBalance(user)

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

    def generate_report(self, user, month):
        start_date = datetime.strptime(month, "%Y-%m")

        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)

        from .models import Transaction

        incomes = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__range=(start_date, end_date)
         )
        expenses = Transaction.objects.filter(
        user=user,
        transaction_type='expense',
        date__range=(start_date, end_date)
        )

        total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
        total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Group expenses by title
        expense_breakdown = expenses.values('title').annotate(total=Sum('amount'))

        return {
        "status": "report_ready",
        "month": month,
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "net_balance": float(total_income - total_expense),
        "pie_chart": list(expense_breakdown),
        "bar_chart": {
            "income": float(total_income),
            "expense": float(total_expense)
        }
    }


class BudgetManager:
    def setBudget(self, user, amount, category_name, start, end):
        category_obj, created = Category.objects.get_or_create(name=category_name)
        Budget.objects.update_or_create(
            user=user,
            category=category_obj,
            defaults={
                'amount': amount,
                'start_date': start,
                'end_date': end
            }
        )

    def calculateRemaining(self, user, category_name):
        category_obj = Category.objects.filter(name=category_name).first()
        if not category_obj:
            raise ValueError(f"Category '{category_name}' not found.")

        budget = Budget.objects.filter(user=user, category=category_obj).first()
        if not budget:
            raise ValueError(f"No budget set for '{category_name}'.")

        # Since Expense has no category, we match by title containing category name
        total_expense = Expense.objects.filter(
            user=user,
            title__icontains=category_name
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        return float(budget.amount) - float(total_expense)