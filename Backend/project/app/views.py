
from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model
from .services import AuthManager, TransactionManager, BudgetManager
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Transaction
from django.db.models import Sum

User = get_user_model()

def index_view(request):

    total_income = Transaction.objects.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'transactions': Transaction.objects.all().order_by('-id')[:5]
    }
    return render(request, 'Budgeteer/index.html', context)

def add_transaction_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        t_type = request.POST.get('type') 
        
        Transaction.objects.create(
            title=title,
            amount=amount,
            transaction_type=t_type
        )
        return redirect('home')
    return render(request, 'Budgeteer/add_transaction.html')

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        manager = AuthManager()
        try:
            user = manager.register(username, email, password)
        except ValueError as e:
            return JsonResponse({'error': 'Missing fields'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Couldn\'t register user'}, status=500)


        return JsonResponse({
            'message': 'User created successfully',
            'user_id': user.id
        }, status=201)
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        manager = AuthManager()
        try:
            manager.login(request, username, password)
        except ValueError as e:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': 'Login failed'}, status=500)

        return JsonResponse({
            'message': 'Login successful'
        })
@method_decorator(csrf_exempt, name='dispatch')
class AddIncomeView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
            
        data = json.loads(request.body)
        manager = TransactionManager()
        
        try:
            income, updated_balance = manager.add_income(
                user=request.user,
                amount=data.get('amount'),
                source=data.get('source'),
                description=data.get('description')
            )
            return JsonResponse({
                'message': 'Income added successfully',
                'income_id': income.id,
                'updatedBalance': str(updated_balance)
            }, status=201)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)  
@method_decorator(csrf_exempt, name='dispatch')       
class AddExpenseView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
            
        data = json.loads(request.body)
        manager = TransactionManager()
        
        try:
            expense, updated_balance = manager.add_expense(
                user=request.user,
                amount=data.get('amount'),
                category_name=data.get('category'), 
                method=data.get('paymentMethod'),
                description=data.get('description')
            )
            
            return JsonResponse({
                'message': 'Expense added successfully',
                'expense_id': expense.id,
                'updatedBalance': str(updated_balance)
            }, status=201)
            
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class SetBudgetView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
        data = json.loads(request.body)
        manager = BudgetManager()
        try:
            manager.setBudget(
                user=request.user,
                amount=data.get('amount'),
                category_name=data.get('category_name'),
                start=data.get('start'),
                end=data.get('end')
            )
            return JsonResponse({'message': 'Budget set successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ViewBalanceView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
        category_name = request.GET.get('category')
        user = request.user
        manager = BudgetManager()
        try:
            remaining = manager.calculateRemaining(user=user, category_name=category_name)
            return JsonResponse({'remaining': remaining}, status=200)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred'}, status=500)



@method_decorator(csrf_exempt, name='dispatch')
class MonthlyReportView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)

        month = request.GET.get('month')  # format: YYYY-MM

        if not month:
            return JsonResponse({'error': 'Month is required'}, status=400)

        manager = TransactionManager()

        try:
            report = manager.generate_report(request.user, month)

            return JsonResponse({
                'message': 'Report ready',
                'data': report
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)