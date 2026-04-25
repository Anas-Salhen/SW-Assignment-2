from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from .models import Income, Expense, Category
from django.db.models import Sum


User = get_user_model()


class AuthManager ():
    def register(username, email, password):
        if not username or not password:
            raise ValueError("Missing fields")
        
        return User.objects.create_user(username, email, password)
            
    def login(self, request, username, password):
        if not username or not password:
            raise ValueError("Missing fields")
            
        user = self.validateCredentials(request, username, password)
        login(request, user)
        
    def validateCredentials(request, username, password):
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