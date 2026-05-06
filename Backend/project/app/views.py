from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import get_user_model, logout
from .services import AuthManager, TransactionManager, BudgetManager
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Transaction
from django.db.models import Sum

User = get_user_model()


# ───────────────────────────────────────────
#  HTML VIEWS
# ───────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/api/home/')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            error = 'Please fill in all fields.'
        else:
            manager = AuthManager()
            try:
                manager.login(request, username, password)
                return redirect('/api/home/')
            except ValueError:
                error = 'Invalid username or password.'
            except Exception:
                error = 'Something went wrong. Please try again.'

    return render(request, 'Budgeteer/login.html', {'error': error})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/api/home/')

    error = None
    success = None

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            error = 'Please fill in all fields.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'
        else:
            manager = AuthManager()
            try:
                manager.register(username, email, password)
                success = 'Account created successfully! You can now login.'
            except Exception:
                error = 'Username already exists or something went wrong.'

    return render(request, 'Budgeteer/register.html', {'error': error, 'success': success})


def logout_view(request):
    logout(request)
    return redirect('/api/login-view/')


def index_view(request):
    if not request.user.is_authenticated:
        return redirect('/api/login-view/')

    total_income = Transaction.objects.filter(
        user=request.user, transaction_type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_expense = Transaction.objects.filter(
        user=request.user, transaction_type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    balance = total_income - total_expense

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'transactions': Transaction.objects.filter(user=request.user).order_by('-id')[:5]
    }
    return render(request, 'Budgeteer/index.html', context)


def add_transaction_view(request):
    if not request.user.is_authenticated:
        return redirect('/api/login-view/')

    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        t_type = request.POST.get('type')

        Transaction.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            transaction_type=t_type
        )
        return redirect('home')

    return render(request, 'Budgeteer/add_transaction.html')


def set_budget_view(request):
    if not request.user.is_authenticated:
        return redirect('/api/login-view/')

    error = None
    success = None

    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        amount = request.POST.get('amount')
        start = request.POST.get('start')
        end = request.POST.get('end')

        if not category_name or not amount or not start or not end:
            error = 'Please fill in all fields.'
        else:
            manager = BudgetManager()
            try:
                manager.setBudget(
                    user=request.user,
                    amount=amount,
                    category_name=category_name,
                    start=start,
                    end=end
                )
                success = f'Budget set successfully for {category_name}!'
            except Exception as e:
                error = str(e)

    return render(request, 'Budgeteer/set_budget.html', {'error': error, 'success': success})


def view_balance_view(request):
    if not request.user.is_authenticated:
        return redirect('/api/login-view/')

    remaining = None
    error = None
    category = request.GET.get('category')

    if category:
        manager = BudgetManager()
        try:
            remaining = manager.calculateRemaining(
                user=request.user,
                category_name=category
            )
        except Exception as e:
            error = str(e)

    return render(request, 'Budgeteer/view_balance.html', {
        'remaining': remaining,
        'error': error
    })


def report_view(request):
    if not request.user.is_authenticated:
        return redirect('/api/login-view/')

    report = None
    error = None
    month = request.GET.get('month')

    if month:
        manager = TransactionManager()
        try:
            report = manager.generate_report(request.user, month)
        except Exception as e:
            error = str(e)

    return render(request, 'Budgeteer/report.html', {
        'report': report,
        'error': error
    })


# ───────────────────────────────────────────
#  API VIEWS
# ───────────────────────────────────────────

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
        except ValueError:
            return JsonResponse({'error': 'Missing fields'}, status=400)
        except Exception:
            return JsonResponse({'error': "Couldn't register user"}, status=500)
        return JsonResponse({'message': 'User created successfully', 'user_id': user.id}, status=201)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        manager = AuthManager()
        try:
            manager.login(request, username, password)
        except ValueError:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception:
            return JsonResponse({'error': 'Login failed'}, status=500)
        return JsonResponse({'message': 'Login successful'})


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
        except Exception:
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
        except Exception:
            return JsonResponse({'error': 'An error occurred'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ViewBalanceView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
        category_name = request.GET.get('category')
        manager = BudgetManager()
        try:
            remaining = manager.calculateRemaining(user=request.user, category_name=category_name)
            return JsonResponse({'remaining': remaining}, status=200)
        except Exception:
            return JsonResponse({'error': 'An error occurred'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class MonthlyReportView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)
        month = request.GET.get('month')
        if not month:
            return JsonResponse({'error': 'Month is required'}, status=400)
        manager = TransactionManager()
        try:
            report = manager.generate_report(request.user, month)
            return JsonResponse({'message': 'Report ready', 'data': report}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)